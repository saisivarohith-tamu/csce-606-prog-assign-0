#!/usr/bin/python3

# test/test_main_create_person.py
import pytest
from unittest.mock import patch
from app import Application
from main import RESTfulTerminalApp
from datetime import datetime

@pytest.fixture
def app_instance():
    return RESTfulTerminalApp()

class TestPersonCreation:

    @patch('builtins.print')
    def test_create_person_success(self, mock_print, app_instance):
        with patch.object(Application, 'create_person', return_value="success"):
            with patch.object(RESTfulTerminalApp, 'generate_session_token', return_value="test_token"):
                # Mocking get_person to return a dictionary with 'updated_at'
                with patch.object(Application, 'get_person', return_value={
                    'username': 'bob',
                    'name': 'Bob',
                    'status': 'feeling good',
                    'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }):
                    # Simulate person creation with valid data
                    app_instance.handle_create(['username="bob"', 'password="password123"', 'name="Bob"', 'status="feeling good"'])

                    # Check that the success path is taken
                    mock_print.assert_any_call("Person\n------")
                    mock_print.assert_any_call("name: Bob")
                    mock_print.assert_any_call("username: bob")
                    mock_print.assert_any_call("status: feeling good")
                    mock_print.assert_any_call("edit: ./app 'session test_token edit'")

                    # Verify that the session was created
                    assert "test_token" in app_instance.sessions
                    assert app_instance.sessions["test_token"].username == "bob"

    def test_create_person_missing_username(self, app_instance):
        result = app_instance.app.create_person(password="wonderland", name="Alice", status="quite small")
        assert result == "failed to create: missing username"

    def test_create_person_missing_password(self, app_instance):
        result = app_instance.app.create_person(username="alice", name="Alice", status="quite small")
        assert result == "failed to create: missing password"

    def test_create_person_missing_name(self, app_instance):
        result = app_instance.app.create_person(username="alice", password="wonderland", status="quite small")
        assert result == "failed to create: missing name"

    def test_create_person_missing_status(self, app_instance):
        result = app_instance.app.create_person(username="alice", password="wonderland", name="Alice")
        assert result == "failed to create: missing status"

    @patch('builtins.print')
    def test_handle_create_missing_username(self, mock_print, app_instance):
        app_instance.handle_create(['password="wonderland"', 'name="Alice"', 'status="quite small"'])
        mock_print.assert_any_call("try harder.\nfailed to create: missing username\nhome: ./app")

    @patch('builtins.print')
    def test_handle_create_missing_password(self, mock_print, app_instance):
        app_instance.handle_create(['username="alice"', 'name="Alice"', 'status="quite small"'])
        mock_print.assert_any_call("try harder.\nfailed to create: missing password\nhome: ./app")

    @patch('builtins.print')
    def test_handle_create_missing_name(self, mock_print, app_instance):
        app_instance.handle_create(['username="alice"', 'password="wonderland"', 'status="quite small"'])
        mock_print.assert_any_call("try harder.\nfailed to create: missing name\nhome: ./app")

    @patch('builtins.print')
    def test_handle_create_missing_status(self, mock_print, app_instance):
        app_instance.handle_create(['username="alice"', 'password="wonderland"', 'name="Alice"'])
        mock_print.assert_any_call("try harder.\nfailed to create: missing status\nhome: ./app")

    @patch('builtins.print')
    def test_create_person_username_too_short(self, mock_print, app_instance):
        result = app_instance.app.create_person(username="ab", password="password123", name="Test User", status="active")
        assert result == "failed to create: username is too short"
    
    @patch('builtins.print')
    def test_create_person_username_too_long(self, mock_print, app_instance):
        long_username = "a" * 21  # 21 characters
        result = app_instance.app.create_person(username=long_username, password="password123", name="Test User", status="active")
        assert result == "failed to create: username is too long"

    @patch('builtins.print')
    def test_create_person_username_invalid_characters(self, mock_print, app_instance):
        invalid_username = "user@name!"  # Contains invalid characters
        result = app_instance.app.create_person(username=invalid_username, password="password123", name="Test User", status="active")
        assert result == "failed to create: invalid username"

    @patch('builtins.print')
    def test_create_person_username_case_insensitivity(self, mock_print, app_instance):
        # First, create a user with a certain case
        result = app_instance.app.create_person(username="Alice", password="password123", name="Alice Smith", status="active")
        assert result == "success"
        
        # Attempt to create another user with a different case for the same username
        result = app_instance.app.create_person(username="alice", password="password456", name="Alice Johnson", status="inactive")
        assert result == "failed to create: alice is already registered"

    @patch('builtins.print')
    def test_create_person_name_too_short(self, mock_print, app_instance):
        result = app_instance.app.create_person(username="testuser", password="password123", name="", status="active")
        assert result == "failed to create: name is too short"

    @patch('builtins.print')
    def test_create_person_name_too_long(self, mock_print, app_instance):
        long_name = "a" * 31  # 31 characters
        result = app_instance.app.create_person(username="testuser", password="password123", name=long_name, status="active")
        assert result == "failed to create: name is too long"

    @patch('builtins.print')
    def test_create_person_name_valid_length(self, mock_print, app_instance):
        valid_name = "John Doe"
        result = app_instance.app.create_person(username="johndoe", password="password123", name=valid_name, status="active")
        assert result == "success"

    @patch('builtins.print')
    def test_create_person_status_too_short(self, mock_print, app_instance):
        result = app_instance.app.create_person(username="testuser", password="password123", name="Valid Name", status="")
        assert result == "failed to create: status is too short"

    @patch('builtins.print')
    def test_create_person_status_too_long(self, mock_print, app_instance):
        long_status = "a" * 101  # 101 characters
        result = app_instance.app.create_person(username="testuser", password="password123", name="Valid Name", status=long_status)
        assert result == "failed to create: status is too long"

    @patch('builtins.print')
    def test_create_person_status_valid_length(self, mock_print, app_instance):
        valid_status = "This is a perfectly valid status."
        result = app_instance.app.create_person(username="validuser", password="password123", name="Valid Name", status=valid_status)
        assert result == "success"