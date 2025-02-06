"""Module containing functions to extract files from an s3 bucket"""
import os
import csv
import boto3
from dotenv import load_dotenv


def download_files(bucket, file_type, substring, name):
    """Download files from the bucket that match the given type and substring."""
    counter = 1
    downloaded_files = []

    for file in bucket.objects.all():
        if file.key.endswith(file_type) and file.key.startswith(substring):
            output_file = f"../data/{name}_data{counter}.{file_type}"
            bucket.download_file(file.key, output_file)
            downloaded_files.append(output_file)
            counter += 1

    return downloaded_files


def combine_csv_files(file_names, output_file):
    """Combine multiple CSV files into a single CSV file."""
    with open(output_file, 'w', newline='', encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        for index, file_name in enumerate(file_names):
            with open(file_name, 'r', encoding="utf-8") as infile:
                reader = csv.reader(infile)

                if index == 0:
                    header = next(reader)
                    writer.writerow(header)
                else:
                    next(reader)

                for row in reader:
                    writer.writerow(row)

            delete_file(file_name)

    return output_file


def delete_file(file_name):
    """Delete a file from the filesystem."""
    try:
        os.remove(file_name)
        return f"DELETED {file_name}"
    except FileNotFoundError:
        return f"File not found, skipping {file_name}"


def get_kiosk_files(bucket):
    """Download and combine kiosk files."""
    substring_kiosk = "lmnh_hist_data_"
    file_names = download_files(bucket, 'csv', substring_kiosk, "kiosk")
    combined_file = combine_csv_files(file_names, "../data/kiosk_data.csv")
    return combined_file, file_names


def get_exhibit_files(bucket):
    """Download exhibit files."""
    substring_exhibit = "lmnh_exhibition_"
    return download_files(bucket, 'json', substring_exhibit, "exhibit")


def setup_aws_session():
    """Setup AWS session."""
    load_dotenv()
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')

    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    return session


def get_files(bucket_name):
    """Main function to get files from S3."""
    session = setup_aws_session()
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)

    kiosk_data = get_kiosk_files(bucket)
    exhibit_data = get_exhibit_files(bucket)

    print("Extract complete")

    return kiosk_data, exhibit_data


if __name__ == "__main__":
    get_files('sigma-resources-museum')
