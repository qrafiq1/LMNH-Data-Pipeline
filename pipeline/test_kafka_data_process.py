# pylint: skip-file
from unittest.mock import patch, MagicMock
import pytest
import logging
from kafka_data_process import validate_message, process_message, consume_event


@pytest.mark.parametrize("data, expected", [
    ({"at": "2024-10-22T10:00:00", "site": "2", "val": 1}, (True, "successful")),
    ({"at": "2024-10-22T10:00:00", "site": "6", "val": 1},
     (False, "Site must be a number between 0 and 5.")),
    ({"at": "2024-10-22T19:00:00", "site": "2",
     "val": 1}, (False, "Out of time bounds")),
    ({"site": "2", "val": 1}, (False, "Timestamp ('at') is missing or None.")),
    ({"at": "2024-10-22T10:00:00", "site": "2", "val": -1},
     (False, 'Val is -1, but "type" key is missing or invalid.')),
    ({"at": "2024-10-22T10:00:00", "site": "2",
     "val": -1, "type": 0}, (True, "successful")),
    ({"at": "2024-10-22T10:00:00", "site": "2", "val": "invalid"},
     (False, "Value must be an integer between -1 and 4.")),
])
def test_validate_message(data, expected):
    assert validate_message(data) == expected


@patch("consumer.import_single_kiosk_data")
@patch("consumer.get_connection")
@patch("consumer.get_cursor")
def test_process_message_valid_message(mock_get_cursor, mock_get_connection, mock_import_single):
    consumer = MagicMock()
    mock_msg = MagicMock()

    mock_msg.key.return_value = None
    mock_msg.value.return_value = b'{"at": "2024-10-22T10:00:00", "site": "2", "val": 1}'
    mock_msg.error.return_value = None

    consumer.poll.return_value = mock_msg

    result = process_message(consumer, mock_get_connection, mock_get_cursor)

    mock_import_single.assert_called_once_with(
        {"at": "2024-10-22T10:00:00", "site": "2",
            "val": 1}, mock_get_connection, mock_get_cursor
    )

    assert result == {"at": "2024-10-22T10:00:00", "site": "2", "val": 1}


@patch("consumer.get_connection")
@patch("consumer.get_cursor")
def test_process_message_invalid_message(mock_get_cursor, mock_get_connection, caplog):
    consumer = MagicMock()
    mock_msg = MagicMock()

    mock_msg.key.return_value = None
    mock_msg.value.return_value = b'{"at": "Invalid", "site": "2", "val": 1}'
    mock_msg.error.return_value = None

    consumer.poll.return_value = mock_msg

    with caplog.at_level(logging.ERROR):
        result = process_message(
            consumer, mock_get_connection, mock_get_cursor)

    assert "Invalid: " in caplog.text
    assert result is None


@patch("consumer.get_connection")
@patch("consumer.get_cursor")
def test_process_message_no_message(mock_get_cursor, mock_get_connection):
    consumer = MagicMock()
    consumer.poll.return_value = None

    result = process_message(consumer, mock_get_connection, mock_get_cursor)

    assert result is None
