"""
Name: test_shared_db.py

Description: Runs unit tests for the shared_db.py library.
"""
# import shared_db
from moto import mock_secretsmanager
import boto3
import unittest
from unittest.mock import Mock, call, patch, MagicMock
import os
import shared_db


class TestSharedDatabseLibraries(unittest.TestCase):
    """
    Runs unit tests for all of the functions in the shared_db library.
    """

    # Create the mock instance of secrets manager
    mock_sm = mock_secretsmanager()

    def setUp(self):
        """
        Perform initial setup for test.
        """
        self.mock_sm.start()
        self.test_sm = boto3.client("secretsmanager")
        self.test_sm.create_secret(
            Name="orcatest-drdb-host", SecretString="aws.postgresrds.host"
        )
        self.test_sm.create_secret(
            Name="orcatest-drdb-admin-pass", SecretString="MySecretAdminPassword"
        )
        self.test_sm.create_secret(
            Name="orcatest-drdb-user-pass", SecretString="MySecretUserPassword"
        )

    def tearDown(self):
        """
        Perform tear down actions
        """
        self.mock_sm.stop()

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ROOT_USER": "postgres",
            "ROOT_DATABASE": "postgres",
        },
        clear=True,
    )
    def test_get_configuration_happy_path(self):
        """
        Testing the rainbows and bunnies path of this call.
        """
        check_config = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "disaster_recovery",
            "root_database": "postgres",
            "app_user": "orcauser",
            "root_user": "postgres",
            "app_user_password": "MySecretUserPassword",
            "root_user_password": "MySecretAdminPassword",
        }

        testing_config = shared_db.get_configuration()

        for key in check_config:
            self.assertIn(key, testing_config)
            self.assertEqual(check_config[key], testing_config[key])

    def test_get_configuration_no_prefix(self):
        """
        Validate an error is thrown if PREFIX is not set.
        """
        error_message = "Environment variable PREFIX is not set."

        with self.assertRaises(Exception) as ex:
            shared_db.get_configuration()
            self.assertEquals(ex.message, error_message)

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ROOT_USER": "postgres",
            "ROOT_DATABASE": "postgres",
        },
        clear=True,
    )
    def test_get_configuration_bad_env(self):
        """
        Validate an error is thrown if an expected environment variable is not
        is not set.
        """
        env_names = [
            "DATABASE_NAME",
            "DATABASE_PORT",
            "APPLICATION_USER",
            "ROOT_USER",
            "ROOT_DATABASE",
        ]
        env_bad_values = [None, ""]
        env_good_value = "This Really Long String"

        for name in env_names:
            for bad_value in env_bad_values:
                with self.subTest(name=name, bad_value=bad_value):
                    # Set the variable to the bad value and create the message
                    if bad_value is None:
                        del os.environ[name]
                    else:
                        os.environ[name] = bad_value

                    message = f"Environment variable {name} is not set and is required"

                    # Run the test
                    with self.assertRaises(Exception) as ex:
                        shared_db.get_configuration()
                        self.assertEquals(ex.message, message)

                    # Reset the value
                    os.environ[name] = env_good_value

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ROOT_USER": "postgres",
            "ROOT_DATABASE": "postgres",
        },
        clear=True,
    )
    def test_get_configuration_bad_secret(self):
        """
        Validates a secret is thrown if a secretmanager ID is invalid.
        """
        secret_keys = [
            "orcatest-drdb-host",
            "orcatest-drdb-admin-pass",
            "orcatest-drdb-user-pass",
        ]
        message = "Failed to retrieve secret manager value."

        for secret_key in secret_keys:
            with self.subTest(secret_key=secret_key):
                # Delete the key
                self.test_sm.delete_secret(
                    SecretId=secret_key, ForceDeleteWithoutRecovery=True
                )

                # Run the test
                with self.assertRaises(Exception) as ex:
                    shared_db.get_configuration()
                    self.assertEquals(ex.message, message)

                # Recreate the key
                self.test_sm.create_secret(
                    Name=secret_key, SecretString="Some-Value-Here"
                )

    @patch.dict(
        os.environ,
        {
            "PREFIX": "orcatest",
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_PORT": "5432",
            "APPLICATION_USER": "orcauser",
            "ROOT_USER": "postgres",
            "ROOT_DATABASE": "postgres",
        },
        clear=True,
    )
    @patch("shared_db._create_connection")
    def test_get_root_connections_database_values(self, mock_connection: MagicMock):
        """
        Tests the function to make sure the correct database value is passed.
        """
        root_db_call = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "postgres",
            "user": "postgres",
            "password": "MySecretAdminPassword",
        }

        user_db_call = {
            "host": "aws.postgresrds.host",
            "port": "5432",
            "database": "disaster_recovery",
            "user": "postgres",
            "password": "MySecretAdminPassword",
        }

        config = shared_db.get_configuration()

        root_db_creds = shared_db.get_root_connection(config)
        mock_connection.assert_called_with(**root_db_call)

        user_db_creds = shared_db.get_root_connection(config, "disaster_recovery")
        mock_connection.assert_called_with(**user_db_call)
