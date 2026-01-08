import unittest
from unittest import mock
from src.fetch import api_response, process_results

#
class FetchTest(unittest.TestCase):

    # test api returning a 200 response
    @mock.patch('src.fetch.requests.get')
    def test_api_response_200(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'Items': []}
        mock_get.return_value = mock_response

        status, retrieved, items = api_response('http://fake-api', 'good_key', 60)
        self.assertEqual(status, 200)
        self.assertEqual(items, [])

    # test api returning 401 response
    @mock.patch('src.fetch.requests.get')
    def test_api_response_401(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'Items': []}
        mock_get.return_value = mock_response

        status, retrieved, items = api_response('http://fake-api', 'bad_key', 60)
        self.assertEqual(status, 401)
        self.assertEqual(items, [])
        self.assertEqual(retrieved, {})


    # test function correctly returning valid data, and ability to navigate it
    @mock.patch('src.fetch.requests.get')
    def test_api_returns_items_matching_total_record_count(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Items": [
                {
                    "Id": 0,
                },
                {
                    "Id": 1
                }
            ],
            "TotalRecordCount": 2,
            "StartIndex": 0
        }
        mock_get.return_value = mock_response

        status, retrieved, items = api_response('http://fake-api', 'good_key', 60)
        self.assertEqual(status, 200)
        self.assertEqual(len(items), retrieved['TotalRecordCount'])

    # test function's to retrieve items and store them in a separate list
    @mock.patch('src.fetch.requests.get')
    def test_api_response_items(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'Items': [
            {'Type': 'VideoPlayback'},
            {'Type': 'SessionEnded'}
        ]}
        mock_get.return_value = mock_response

        status, retrieved, items = api_response('http://fake-api', 'good_key', 60)
        self.assertEqual(status, 200)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['Type'], 'VideoPlayback')

    @mock.patch('src.fetch.requests.get')
    def test_api_request_contains_auth_and_min_date(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'Items': []}
        mock_get.return_value = mock_response

        api_response('http://fake-api', 'good_key', 60)

        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args

        self.assertEqual(kwargs['headers']['X-Emby-Token'], 'good_key')
        self.assertIn('minDate', kwargs['params'])

    @mock.patch('src.fetch.requests.get')
    def test_api_response_missing_items_key(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        status, retrieved, items = api_response('http://fake-api', 'good_key', 60)

        self.assertEqual(items, [])


    @mock.patch('src.fetch.api_response')
    def test_process_results(self, mock_api_call):
        mock_api_call.return_value = 200, {}, []

        value = process_results('http://fake-api', 'good_key', 60)
        mock_api_call.assert_called_once()
        self.assertTrue(value)
