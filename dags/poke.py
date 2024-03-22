import logging
import pendulum
import requests
import os
import boto3
import io
import dotenv

from airflow.decorators import dag, task, task_group
import polars as pl
import duckdb
from duckdb.typing import VARCHAR

from include.data_validation import Pokemon, validate_df
from include.client import connection

logger = logging.getLogger(__name__)
dotenv.load_dotenv(dotenv.find_dotenv())

@dag(start_date=pendulum.now())
def poke_pipeline():
    
    @task
    def fetch_pokemon_urls() -> dict:
        url = 'https://pokeapi.co/api/v2/pokemon?limit=493'
        response = requests.get(url)
        if response.status_code == 200:
            urls = response.json()
            return urls
        else:
            raise Exception("Failed to fetch data from PokeAPI")
        
    @task
    def download_pokemon_data(urls: dict):
        pokemons = []

        for pokemon in urls["results"]:
            name = pokemon["name"]
            url = pokemon["url"]
            pokemon_data = requests.get(url).json()
            abilities = [ability["ability"]["name"] for ability in pokemon_data["abilities"]]
            types = [ptype["type"]["name"] for ptype in pokemon_data["types"]]
            height = pokemon_data["height"]
            weight = pokemon_data["weight"]
            pokemons.append({"Name": name, "Abilities": abilities, "Types": types, "Height": height, "Weight": weight})

        df = pl.DataFrame(pokemons)

        validate_df(df, Pokemon)

        client = connection()
        
        pq_io = io.BytesIO()
        df.write_parquet(pq_io)
        pq_io.seek(0)

        buckets = [bucket["Name"] for bucket in client.list_buckets()["Buckets"]]
        if 'raw' not in buckets:
            client.create_bucket(Bucket='raw')
        client.upload_fileobj(
            pq_io,
            Bucket='raw',
            Key='pokemon.parquet'
        )
        
    @task
    def read_to_db():
        with duckdb.connect(database='pokemon.db') as conn:
            conn.execute('INSTALL httpfs')
            conn.execute('LOAD httpfs')
            conn.execute('SET s3_url_style="path"')
            conn.execute('SET s3_endpoint="host.docker.internal:9000"')
            conn.execute('SET s3_use_ssl=false')
            conn.execute(f'SET s3_access_key_id={os.getenv("AWS_ACCESS_KEY_ID")}')
            conn.execute(f'SET s3_secret_access_key={os.getenv("AWS_SECRET_ACCESS_KEY")}')

            conn.sql("""
                     CREATE OR REPLACE TABLE pokemon_raw AS
                     SELECT *
                     FROM read_parquet('s3://raw/pokemon.parquet')
                     """)
            
    @task
    def add_units_to_height_and_weight():
        with duckdb.connect(database='pokemon.db') as conn:
            conn.sql("""
                    DROP TABLE IF EXISTS pokemon_transformed;
                    CREATE TABLE pokemon_transformed AS
                    SELECT
                        height as height_decimeter,
                        weight as weight_hectogram
                    FROM pokemon_raw""")
        
    @task
    def abilities_frequency():
        with duckdb.connect(database='pokemon.db') as conn:
            conn.sql("""
                     SELECT
                        ability,
                        COUNT(*) AS freq
                     FROM (
                        SELECT UNNEST(abilities) AS ability
                        FROM pokemon_raw
                     ) AS subquery
                     GROUP BY ability
                     ORDER BY freq DESC
                     LIMIT 20
                     """)
                
    @task_group
    def extract_load():
        urls = fetch_pokemon_urls()
        download_pokemon_data(urls) >> read_to_db()

    @task_group
    def transform():
        add_units_to_height_and_weight() >> abilities_frequency()

    extract_load() >> transform()

poke_pipeline()
