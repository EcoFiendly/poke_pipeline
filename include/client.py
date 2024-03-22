import boto3
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv())

def connection() -> boto3.client:
    return boto3.client('s3',
                        endpoint_url=os.getenv("MINIO_ENDPOINT_URL"),
                        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                        use_ssl=False
                        )