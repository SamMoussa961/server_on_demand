import subprocess
import unittest
from unittest import mock
from src.wake_server import ping_host, check_and_wake

class TestWakeServer(unittest.TestCase):

    # test for a reachable host
    @mock.patch('src.wake_server.subprocess.run')
    def test_ping_server_ping_reachable(self, mock_run):
        mock_run.return_value.returncode=0

        value = ping_host('127.0.0.1')
        self.assertTrue(value)

    # test for an unreachable host
    @mock.patch('src.wake_server.subprocess.run')
    def test_ping_server_ip_unreachable(self, mock_run):
        mock_run.return_value.returncode = 1

        value = ping_host('127.0.0.1')
        self.assertFalse(value)

    # test function for an invalid ip address
    @mock.patch('src.wake_server.subprocess.run')
    def test_ping_host_invalid_ip(self, mock_run):
        value = ping_host('0.1')
        self.assertFalse(value)

        mock_run.assert_not_called()

    # test it timeouts after set number
    @mock.patch('src.wake_server.subprocess.run')
    def test_ping_host_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=['ping', '-c', '1', '127.0.0.1'],
            timeout=10
        )
        value = ping_host('127.0.0.1', timeout=10)

        self.assertFalse(value)
        mock_run.assert_called_once()


    @mock.patch('src.wake_server.ping_host', return_value=True)
    def test_wake_server_pc_is_up(self, mock_ping_host):

        ip_address = '127.0.0.1'
        mac_address = '00:11:22:33:44:55'
        broadcast_address = '192.168.1.1'

        value = check_and_wake(ip_address, mac_address, broadcast_address)
        self.assertTrue(value)


    @mock.patch('src.wake_server.ping_host', return_value=False)
    @mock.patch('src.wake_server.send_magic_packet')
    def test_wake_server_is_down(self, mock_send_magic_packet, mock_ping_host):
        ip_address = '127.0.0.1'
        mac_address = '00:11:22:33:44:55'
        broadcast_address = '192.168.1.1'

        value = check_and_wake(ip_address, mac_address, broadcast_address)
        self.assertTrue(value)

        mock_send_magic_packet.assert_called_once_with(
            mac_address,
            ip_address=broadcast_address
        )