"""Collects data from kafka cluster, cleans it, and loads it to rds db."""
from os import environ
import logging
import argparse
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from confluent_kafka import Consumer
from etl_pipeline import get_connection, get_cursor, import_single_kiosk_data


TOPIC = "lmnh"
FILE_NAME = "consumer_logs.txt"


def setup_logging(log_to_file: bool) -> None:
    """Configures logging settings."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR if log_to_file else logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    if log_to_file:
        file_handler = logging.FileHandler(FILE_NAME, mode='a')
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)


def validate_message(data: dict) -> tuple[bool, str]:
    """Validates the message data."""
    try:
        date = data.get("at")

        if date is None:
            return False, "Timestamp ('at') is missing or None."

        try:
            date = datetime.fromisoformat(date)
        except ValueError as e:
            return False, "Date is invalid datetime format"

        start_time = date.replace(hour=9, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=18, minute=0, second=0, microsecond=0)

        now = datetime.now()
        now = now.replace(tzinfo=timezone.utc)
        if date > now:
            return False, "Date cannot be in the future"

        if date < start_time or date > end_time:
            return False, "Out of time bounds"

        site = data["site"]
        if not site.isdigit() or not 0 <= int(site) <= 5:
            return False, "Site must be a number between 0 and 5."

        val = data["val"]
        if not isinstance(val, int) or not -1 <= val <= 4:
            return False, "Value must be an integer between -1 and 4."

        if val == -1:
            if "type" not in data or data["type"] not in [0, 1]:
                return False, 'Val is -1, but "type" key is missing or invalid.'

        return True, "successful"
    except KeyError as e:
        return False, f"Missing key {e}"


def process_message(consumer, conn, cursor):
    """Processes a single message from the consumer."""
    msg = consumer.poll(1.0)

    if msg is None:
        print("Waiting...")
        return None
    elif msg.error():
        logging.error("ERROR: %s", msg.error())
        return None

    key = msg.key().decode("utf-8") if msg.key() is not None else None
    value = msg.value().decode("utf-8") if msg.value() is not None else None

    value_dict = json.loads(value)
    is_valid, message = validate_message(value_dict)

    if not is_valid:
        logging.error("Invalid: %s", message)
        return None

    logging.info(f"""Consumed event from topic {
                 msg.topic()}: key = {key} value = {value}""")

    import_single_kiosk_data(value_dict, conn, cursor)

    return value_dict


def consume_event(consumer: Consumer):
    """Consumes data from kafka cluster, validates it and calls function to load it."""
    conn = get_connection()
    cursor = get_cursor(conn)

    while True:
        process_message(consumer, conn, cursor)


if __name__ == "__main__":

    load_dotenv('.env.kafka')

    parser = argparse.ArgumentParser(description="consume messages")
    parser.add_argument("--logs", action="store_true",
                        help="Output logs to a file")

    args = parser.parse_args()

    setup_logging(args.logs)

    bootstrap_servers = environ['BOOTSTRAP_SERVERS']
    security_protocol = environ['SECURITY_PROTOCOL']
    sasl_mechanism = environ['SASL_MECHANISM']
    sasl_username = environ['USERNAME']
    sasl_password = environ['PASSWORD']

    kafka_config = {
        'bootstrap.servers': bootstrap_servers,
        'security.protocol': security_protocol,
        'sasl.mechanisms': sasl_mechanism,
        'sasl.username': sasl_username,
        'sasl.password': sasl_password,
        'group.id': 'c14-qasim-consumer',
        'auto.offset.reset': 'earliest',
    }

    consumer_ = Consumer(kafka_config)

    consumer_.subscribe([TOPIC])

    try:
        consume_event(consumer_)
    except KeyboardInterrupt:
        pass
    finally:
        consumer_.close()
