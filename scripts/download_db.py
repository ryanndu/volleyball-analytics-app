import boto3
import os

S3_BUCKET = os.environ["S3_BUCKET"]
S3_KEY = os.environ.get("S3_KEY", "volleyball.duckdb")
LOCAL_PATH = "data/volleyball.duckdb"

def download_db():
    print(f"Downloading {S3_KEY} from {S3_BUCKET}...")
    s3 = boto3.client("s3")
    os.makedirs("data", exist_ok=True)
    s3.download_file(S3_BUCKET, S3_KEY, LOCAL_PATH)
    print("Database downloaded successfully.")

if __name__ == "__main__":
    download_db()