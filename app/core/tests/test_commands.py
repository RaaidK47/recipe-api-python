"""Test custom Django management commands."""

from unittest.mock import patch  # Mock behaviour of Database. Simulate that DB is returning response or not # noqa: E501

from psycopg2 import OperationalError as Psycopg2Error  # OperationalError Exception: posibility of error we might get when we try to connect to DB befor it is ready # noqa: E501

from django.core.management import call_command  # Helper Function Provided by Django: Call the command that we are testing # noqa: E501
from django.db.utils import OperationalError    # Helper Function Provided by Django: Check if DB is ready or not # noqa: E501
from django.test import SimpleTestCase          # Helper Function Provided by Django: Base Test Class (Just checking DB availability) # noqa: E501


@patch('core.management.commands.wait_for_db.Command.check')  # Mock the behaviour of check() function (Status of Database) # noqa: E501
# ^Decorator ^ Command that we are mocking
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        # patched_check = magic mock object that replaces check by patch

        """Test waiting for database if database ready."""
        patched_check.return_value = True
        # ^when check is called inside our command, inside our test case, we just want it to return the True value. # noqa: E501

        call_command('wait_for_db')  # Call the command that we are testing

        patched_check.assert_called_once_with(databases=['default'])  # Check if the check() method has been called # noqa: E501
        # ^checks that we're calling the right thing from our wait_for_db ready. # noqa: E501

    @patch('time.sleep')  # Mock the behaviour of time.sleep() function
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
        #
        # ^How Mocking works when when you want to raise an exception (when a Database is not ready) # noqa: E501
        # The way that you make it raise an exception instead of actually pretend to get value is you use the side effect. # noqa: E501
        # side_effect allows you to pass in various different items that get handled differently depending on that type. # noqa: E501
        # First '2' times Psycopg2Error, then '3' times OperationalError, then True (6th time). # noqa: E501
        # Psycopg2Error > Database not even started yet
        # OperationalError > Database is started but not ready to accept connections yet # noqa: E501
        # '2' and '3' arbitary values based on trial and error / experience

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        # ^check if the check() method has been called 6 times

        patched_check.assert_called_with(databases=['default'])
