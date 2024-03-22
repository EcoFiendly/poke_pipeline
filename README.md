# Poke Pipeline example

Small ELT pipeline using pokeapi

# Architecture

API: pokeapi \
Object storage: Minio \
OLAP db: duckdb \
Orchestrator: Astronomer Airflow

# Deploy Your Project Locally

1. Start Airflow on your local machine by running 'astro dev start'.

This command will spin up 5 Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- Triggerer: The Airflow component responsible for triggering deferred tasks
- Minio: The object storage for storing the raw data

2. Verify that all 5 Docker containers were created by running 'docker ps'.

Note: Running 'astro dev start' will start your project with the Airflow Webserver exposed at port 8080, Postgres exposed at port 5432 and Minio exposed at port 9090. If you already have either of those ports allocated, you can either [stop your existing Docker containers or change the port](https://docs.astronomer.io/astro/test-and-troubleshoot-locally#ports-are-not-available).

3. Access the Airflow UI for your local Airflow project. To do so, go to http://localhost:8080/ and log in with 'admin' for both your Username and Password.

4. Access the Minio UI for your local Airflow project. To do so, go to http://localhost:9090/ and log in with 'minioadmin' for both your Username and Password

You should also be able to access your Postgres Database at 'localhost:5432/postgres'.
