import subprocess
import unittest
from unittest import mock

from src.shutdown_server import shutdown_server


class TestShutdownServer(unittest.TestCase):

    @mock.patch('src.shutdown_server.subprocess.run')
    def test_shutdown_success(self, mock_run):
        ip = '127.0.0.1'
        ssh_user = 'mock-user'
        mock_run.return_value.returncode = 0

        value = shutdown_server(ip, ssh_user)
        self.assertTrue(value)

        mock_run.assert_called_once_with(
            ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=5',
             f'{ssh_user}@{ip}', 'sudo', 'shutdown', 'now'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )

    @mock.patch('src.shutdown_server.subprocess.run')
    def test_shutdown_failure(self, mock_run):
        mock_run.return_value.returncode = 1

        value = shutdown_server('127.0.0.1')
        self.assertFalse(value)

    @mock.patch('src.shutdown_server.subprocess.run')
    def test_shutdown_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=5',
                 'mock-user@127.0.0.1', 'sudo', 'shutdown', 'now'],
            timeout=10,
        )

        value = shutdown_server('127.0.0.1')
        self.assertFalse(value)
        mock_run.assert_called_once()

    @mock.patch('src.shutdown_server.subprocess.run')
    def test_shutdown_invalid_ip(self, mock_run):
        value = shutdown_server('0.1')
        self.assertFalse(value)
        mock_run.assert_not_called()
