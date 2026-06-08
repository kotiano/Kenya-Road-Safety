import boto3
import os
from pathlib import Path

BUCKET = os.environ["AWS_BUCKET"]
PREFIX = "ntsa/raw"          
DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

s3 = boto3.client("s3")


def upload_file(local_path: Path, s3_key: str):
    print(f"  uploading {local_path.name} → s3://{BUCKET}/{s3_key}")
    s3.upload_file(
        str(local_path),
        BUCKET,
        s3_key,
        ExtraArgs={"ContentType": "text/csv"},
    )


def main():
    csvs = list(DATA_DIR.glob("*.csv"))
    if not csvs:
        print(f"No CSVs found in {DATA_DIR}")
        return

    print(f"Uploading {len(csvs)} files to s3://{BUCKET}/{PREFIX}/\n")
    for f in sorted(csvs):
        upload_file(f, f"{PREFIX}/{f.name}")

    print(f"\nDone. Check with: aws s3 ls s3://{BUCKET}/{PREFIX}/")


if __name__ == "__main__":
    main()
