# pylint: skip-file
import unittest
from unittest.mock import MagicMock, patch
import os
import csv

from s3_data_download import download_files, delete_file, get_kiosk_files, get_exhibit_files, setup_aws_session, get_files


class TestFileOperations(unittest.TestCase):

    @patch('extract.boto3.Session')
    def test_download_files(self, mock_boto_session):
        # Setup mocks
        mock_bucket = MagicMock()
        mock_bucket.objects.all.return_value = [
            MagicMock(key='lmnh_hist_data_1.csv'),
            MagicMock(key='lmnh_hist_data_2.csv')
        ]

        mock_session = MagicMock()
        mock_session.resource.return_value.Bucket.return_value = mock_bucket
        mock_boto_session.return_value = mock_session

        # Mock file download
        mock_bucket.download_file = MagicMock()

        downloaded_files = download_files(
            mock_bucket, 'csv', "lmnh_hist_data_", "kiosk")

        # Assert calls and output
        self.assertEqual(downloaded_files, [
                         '../data/kiosk_data1.csv', '../data/kiosk_data2.csv'])
        self.assertTrue(mock_bucket.download_file.called)

    @patch('extract.os.remove')
    def test_delete_file(self, mock_os_remove):
        # Test deleting a file successfully
        mock_os_remove.return_value = None
        result = delete_file("test_file.csv")
        self.assertEqual(result, "DELETED test_file.csv")
        mock_os_remove.assert_called_with("test_file.csv")

        # Test file not found scenario
        mock_os_remove.side_effect = FileNotFoundError
        result = delete_file("missing_file.csv")
        self.assertEqual(result, "File not found, skipping missing_file.csv")

    @patch('extract.boto3.Session')
    def test_get_kiosk_files(self, mock_boto_session):
        # Setup mocks
        mock_bucket = MagicMock()
        mock_bucket.objects.all.return_value = [
            MagicMock(key='lmnh_hist_data_1.csv'),
            MagicMock(key='lmnh_hist_data_2.csv')
        ]

        mock_session = MagicMock()
        mock_session.resource.return_value.Bucket.return_value = mock_bucket
        mock_boto_session.return_value = mock_session

        # Mock file downloads
        mock_bucket.download_file = MagicMock()
        with patch('extract.combine_csv_files', return_value="../data/kiosk_data.csv"):
            combined_file, file_names = get_kiosk_files(mock_bucket)

        # Assert results
        self.assertEqual(
            file_names, ['../data/kiosk_data1.csv', '../data/kiosk_data2.csv'])
        self.assertEqual(combined_file, "../data/kiosk_data.csv")

    @patch('extract.boto3.Session')
    def test_get_exhibit_files(self, mock_boto_session):
        # Setup mocks
        mock_bucket = MagicMock()
        mock_bucket.objects.all.return_value = [
            MagicMock(key='lmnh_exhibition_1.json'),
            MagicMock(key='lmnh_exhibition_2.json')
        ]

        mock_session = MagicMock()
        mock_session.resource.return_value.Bucket.return_value = mock_bucket
        mock_boto_session.return_value = mock_session

        # Mock file downloads
        mock_bucket.download_file = MagicMock()

        exhibit_files = get_exhibit_files(mock_bucket)

        # Assert results
        self.assertEqual(
            exhibit_files, ['../data/exhibit_data1.json', '../data/exhibit_data2.json'])

    @patch('extract.boto3.Session')
    def test_setup_aws_session(self, mock_boto_session):
        # Assuming environment variables are set
        mock_boto_session.return_value = MagicMock()

        session = setup_aws_session()

        self.assertIsNotNone(session)

    @patch('extract.get_kiosk_files')
    @patch('extract.get_exhibit_files')
    @patch('extract.setup_aws_session')
    def test_get_files(self, mock_setup_aws_session, mock_get_exhibit_files, mock_get_kiosk_files):
        # Mock AWS session
        mock_setup_aws_session.return_value = MagicMock()

        mock_get_kiosk_files.return_value = (
            '../data/kiosk_data.csv', ['../data/kiosk_data1.csv'])
        mock_get_exhibit_files.return_value = ['../data/exhibit_data1.json']

        result = get_files('test-bucket')

        # Assert the result
        self.assertEqual(result, (('../data/kiosk_data.csv',
                         ['../data/kiosk_data1.csv']), ['../data/exhibit_data1.json']))
        mock_get_kiosk_files.assert_called_once()
        mock_get_exhibit_files.assert_called_once()


if __name__ == "__main__":
    unittest.main()
