# pylint: skip-file
import pytest
import psycopg2
from unittest.mock import patch, MagicMock, mock_open

from etl_pipeline import load_csv, get_connection, get_cursor, import_request_interactions, import_rating_interactions, import_kiosk_data


def test_load_csv():
    mock_csv_data = "column1,column2\nvalue1,value2\nvalue3,value4\n"

    with patch("builtins.open", mock_open(read_data=mock_csv_data)):
        result = load_csv("fake_path.csv")

        expected_result = [
            {"column1": "value1", "column2": "value2"},
            {"column1": "value3", "column2": "value4"},
        ]

        assert result == expected_result


def test_load_csv_empty_file():
    with patch("builtins.open", mock_open(read_data="")):
        result = load_csv("fake_path.csv")

        expected_result = []

        assert result == expected_result


@patch('psycopg2.connect')
def test_get_connection(mock_connect):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    conn = get_connection()

    mock_connect.assert_called_once()
    assert conn == mock_conn


@patch('psycopg2.connect')
def test_get_cursor(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    conn = get_connection()
    cursor = get_cursor(conn)

    mock_conn.cursor.assert_called_once_with(
        cursor_factory=psycopg2.extras.RealDictCursor)
    assert cursor == mock_cursor


@patch('psycopg2.connect')
def test_import_request_interactions(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    event_at = "2024-01-01 00:00:00"
    request_id = 1
    exhibit_id = 2

    import_request_interactions(
        event_at, request_id, exhibit_id, mock_conn, mock_cursor)

    mock_cursor.execute.assert_called_once_with(
        """INSERT INTO request_interaction (exhibition_id, request_id, event_at) VALUES (%s, %s, %s)""", (
            exhibit_id, request_id, event_at)
    )
    mock_conn.commit.assert_called_once()


@patch('psycopg2.connect')
def test_import_rating_interactions(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    event_at = "2024-01-01 00:00:00"
    rating_id = 2
    exhibit_id = 3

    import_rating_interactions(
        event_at, rating_id, exhibit_id, mock_conn, mock_cursor)

    mock_cursor.execute.assert_called_once_with(
        """INSERT INTO rating_interaction (exhibition_id, rating_id, event_at) VALUES (%s, %s, %s)""", (
            exhibit_id, rating_id, event_at)
    )
    mock_conn.commit.assert_called_once()


@patch('psycopg2.connect')
def test_import_request_interactions_error(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Database error")

    event_at = "2024-01-01 00:00:00"
    request_id = 1
    exhibit_id = 2

    with pytest.raises(Exception):
        import_request_interactions(
            event_at, request_id, exhibit_id, mock_conn, mock_cursor)


@patch('psycopg2.connect')
def test_import_rating_interactions_error(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Database error")

    event_at = "2024-01-01 00:00:00"
    rating_id = 2
    exhibit_id = 3

    with pytest.raises(Exception):
        import_rating_interactions(
            event_at, rating_id, exhibit_id, mock_conn, mock_cursor)


@patch('psycopg2.connect')
@patch('pipeline.load_csv')
def test_import_kiosk_data(mock_load_csv, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_load_csv = [
        {"at": "2024-01-01 00:00:00", "val": "-1", "type": "1", "site": "2"},
        {"at": "2024-01-02 00:00:00", "val": "5", "site": "1"}
    ]

    with patch("builtins.open", mock_open(read_data='at,val,site,type\n2024-01-01 00:00:00,1,1,0\n2024-01-01 01:00:00,-1,2,1')):

        import_kiosk_data(mock_load_csv, mock_conn, mock_cursor)

        mock_cursor.execute.assert_any_call(
            "SELECT request_id FROM request WHERE request_value = %s", (1,))
        mock_cursor.execute.assert_any_call(
            "SELECT rating_id FROM rating WHERE rating_value = %s", (5,))

        assert mock_cursor.fetchone.call_count == 2
        assert mock_conn.commit.call_count == 4
