import unittest
from unittest import mock

from src.controller import ensure_awake, controller


class TestController(unittest.TestCase):

    #
    @mock.patch("src.controller.ping_host", return_value=True)
    def test_ensure_awake(self, mock_ping_host):
        ip_address = '127.0.0.1'

        value = ensure_awake(ip_address)
        self.assertTrue(value)
        mock_ping_host.assert_called_once_with(ip_address)

    #
    @mock.patch("src.controller.ping_host", return_value=False)
    def test_ensure_awake_returns_false_when_host_down(self, mock_ping_host):
        ip_address = '127.0.0.1'

        value = ensure_awake(ip_address)
        self.assertFalse(value)
        mock_ping_host.assert_called_once_with(ip_address)

    # test condition: user active, server up
    # test: assert process results is called once, assert ensure awake is called once, do nothing
    @mock.patch("src.controller.process_results", return_value=False)
    @mock.patch("src.controller.ensure_awake")
    @mock.patch("src.controller.send_magic")
    def test_controller_found_no_active_user(self, mock_send_magic, mock_ensure_awake, mock_process_results):
        ip_address = '127.0.0.1'
        mac_address = '12:34:56:78:90:AB'
        broadcast_address = '192.168.1.255'
        api_url = "http://fake-url.com"
        api_key = "fake-key"
        how_long = 60

        value = controller(ip_address, mac_address, broadcast_address, api_url, api_key, how_long)
        self.assertEqual(value, "no_activity")

        mock_ensure_awake.assert_not_called()
        mock_process_results.assert_called_once()
        mock_send_magic.assert_not_called()

    # test condition: user active, server down
    # test: assert process results is called once, assert ensure awake is called once, assert magic is sent
    @mock.patch("src.controller.process_results", return_value=True)
    @mock.patch("src.controller.ensure_awake", return_value=False)
    @mock.patch("src.controller.send_magic", return_value=True)
    def test_controller_found_active_user_server_off_wol_sent(self, mock_send_magic, mock_ensure_awake, mock_process_results):
        ip_address = '127.0.0.1'
        mac_address = '12:34:56:78:90:AB'
        broadcast_address = '192.168.1.255'
        api_url = "http://fake-url.com"
        api_key = "fake-key"
        how_long = 60

        value = controller(ip_address, mac_address, broadcast_address, api_url, api_key, how_long)
        self.assertEqual(value, "wol_sent")

        mock_send_magic.assert_called_once()
        mock_ensure_awake.assert_called_once()
        mock_process_results.assert_called_once()

    @mock.patch("src.controller.process_results", return_value=True)
    @mock.patch("src.controller.ensure_awake", return_value=False)
    @mock.patch("src.controller.send_magic", return_value=False)
    def test_controller_found_active_user_server_off_wol_failed(self, mock_send_magic, mock_ensure_awake, mock_process_results):
        ip_address = '127.0.0.1'
        mac_address = '12:34:56:78:90:AB'
        broadcast_address = '192.168.1.255'
        api_url = "http://fake-url.com"
        api_key = "fake-key"
        how_long = 60

        value = controller(ip_address, mac_address, broadcast_address, api_url, api_key, how_long)
        self.assertEqual(value, "wol_failed")

        mock_send_magic.assert_called_once()
        mock_ensure_awake.assert_called_once()
        mock_process_results.assert_called_once()


    # test condition: user active, server up
    # test: assert process results is called once, assert ensure awake is called once, do nothing
    @mock.patch("src.controller.process_results", return_value=True)
    @mock.patch("src.controller.ensure_awake", return_value=True)
    @mock.patch("src.controller.send_magic")
    def test_controller_found_active_user_server_on(self, mock_send_magic, mock_ensure_awake, mock_process_results):
        ip_address = '127.0.0.1'
        mac_address = '12:34:56:78:90:AB'
        broadcast_address = '192.168.1.255'
        api_url = "http://fake-url.com"
        api_key = "fake-key"
        how_long = 60

        value = controller(ip_address, mac_address, broadcast_address, api_url, api_key, how_long)
        self.assertEqual(value, "already_on")

        mock_ensure_awake.assert_called_once()
        mock_process_results.assert_called_once()
        mock_send_magic.assert_not_called()



# controller checks process results, there is no user? ensure awake, up? shutdown! LATER
