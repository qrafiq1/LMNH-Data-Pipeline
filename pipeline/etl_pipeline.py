"""Pipeline that extracts data from an s3 bucket, transforms it and uploads it to an RDS db."""
import csv
import logging
import argparse
from os import environ
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection, cursor
from s3_data_download import get_files


KIOSK_DATA_PATH = "../data/kiosk_data.csv"
SCHEMA_FILE_PATH = "./schema.sql"
LOGS_NAME = "./pipeline_logs.log"


def load_csv(filepath: str) -> list[dict]:
    """Loads the local csv file"""
    logging.info("Loading data from %s", filepath)
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        kiosk_data = []
        for row in reader:
            kiosk_data.append(row)
    logging.info("Loaded %s entries from CSV", len(kiosk_data))
    return kiosk_data


def get_connection():
    """Connects to the database"""
    logging.info("Connecting to the database")
    load_dotenv(".env")
    try:
        conn = psycopg2.connect(
            database=environ["DATABASE_NAME"],
            user=environ["DATABASE_USERNAME"],
            password=environ["DATABASE_PASSWORD"],
            host=environ["DATABASE_IP"],
            port=environ["DATABASE_PORT"]
        )
        logging.info("Database connection established")
        return conn
    except Exception as e:
        logging.error("Failed to connect to the database: %s", e)
        raise


def get_cursor(conn):
    """Gets the cursor"""
    logging.info("Creating database cursor")
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return cursor
    except Exception as e:
        logging.error("Failed to create cursor: %s", e)
        raise


def get_request_id(request_type: int, conn, cursor) -> int:
    """Gets the request ID"""
    try:
        cursor.execute(
            "SELECT request_id FROM request WHERE request_value = %s", (request_type,))
        conn.commit()
        request_id = cursor.fetchone().get("request_id")
        logging.info("Request ID %s found for type %s",
                     request_id, request_type)
        return request_id
    except Exception as e:
        logging.error("Failed to get request ID: %s", e)
        raise


def get_rating_id(value: int, conn, cursor) -> int:
    """Gets the rating ID"""
    try:
        cursor.execute(
            "SELECT rating_id FROM rating WHERE rating_value = %s", (value,))
        conn.commit()
        rating_id = cursor.fetchone().get("rating_id")
        logging.info("Rating ID %s", rating_id)
        return rating_id
    except Exception as e:
        logging.error("Failed to get rating ID: %s", e)
        raise


def import_request_interactions(event_at, request_id: int, exhibit_id: int,
                                conn, cursor) -> None:
    """Imports a request interaction into the database"""
    try:
        cursor.execute(
            """INSERT INTO request_interaction (exhibition_id, request_id, event_at) VALUES (%s, %s, %s)""", (
                exhibit_id, request_id, event_at)
        )
        conn.commit()
        logging.info(
            "Imported request interaction for exhibit %s at %s", exhibit_id, event_at)
    except Exception as e:
        cursor.connection.rollback()
        logging.error("Failed to import request interaction: %s", e)
        raise Exception("Error") from e


def import_rating_interactions(event_at, rating_id: int, exhibit_id: int,
                               conn, cursor) -> None:
    """Imports a rating interaction into the database"""
    try:
        cursor.execute(
            """INSERT INTO rating_interaction (exhibition_id, rating_id, event_at) VALUES (%s, %s, %s)""", (
                exhibit_id, rating_id, event_at)
        )
        conn.commit()
        logging.info(
            "Imported rating interaction for exhibit %s at %s", exhibit_id, event_at)
    except Exception as e:
        cursor.connection.rollback()
        logging.error("Failed to import rating interaction: %s", e)
        raise Exception("Error") from e


def import_kiosk_data(entries: list[dict], conn, cursor, limit=None) -> None:
    """Inserts kiosk data into the database"""
    logging.info("Starting import of kiosk data")

    for entry in entries[:limit]:
        import_single_kiosk_data(entry, conn, cursor)

    logging.info("Finished importing kiosk data")


def import_single_kiosk_data(entry: dict, conn, cursor) -> None:
    event_at = entry["at"]
    value_id = int(entry["val"])
    exhibit_id = int(entry["site"]) + 1

    if value_id == -1:
        request_type = int(float(entry["type"]))
        request_id = get_request_id(request_type, conn, cursor)
        import_request_interactions(
            event_at, request_id, exhibit_id, conn, cursor)
    else:
        rating_id = get_rating_id(value_id, conn, cursor)
        import_rating_interactions(
            event_at, rating_id, exhibit_id, conn, cursor)
    logging.info("Finished importing kiosk data")


def reset_database(schema_file_path: str, cursor, conn):
    """Resets the RDS database"""
    with open(schema_file_path, 'r', encoding="utf-8") as schema:
        sql_command = schema.read()

    cursor.execute(sql_command)
    conn.commit()
    logging.info("Database reset.")


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Import kiosk data into the database.")
    parser.add_argument(
        "-b", "--bucket",
        required=True,
        help="Name of the AWS bucket"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of rows to upload"
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Output logs to a file instead of console"
    )
    return parser.parse_args()


def configure_logging(to_file: bool) -> None:
    """Configures logging settings."""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    if to_file:
        logging.basicConfig(
            filename=LOGS_NAME,
            filemode='w',
            level=logging.INFO,
            format=log_format
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format=log_format
        )


def main():
    """Calls all necessary functions for the pipeline"""
    args = parse_arguments()
    configure_logging(args.logs)

    get_files(args.bucket)

    conn = get_connection()
    cursor_ = get_cursor(conn)

    reset_database(SCHEMA_FILE_PATH, cursor_, conn)

    kiosk_data = load_csv(KIOSK_DATA_PATH)
    import_kiosk_data(kiosk_data, conn, cursor_, args.limit)

    conn.close()
    cursor_.close()
    logging.info("Data import process completed")


if __name__ == "__main__":
    main()
