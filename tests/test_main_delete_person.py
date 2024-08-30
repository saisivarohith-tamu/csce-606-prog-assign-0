#!/usr/bin/python3

# test/test_main_delete_person.py
import pytest
from unittest.mock import patch, MagicMock
from main import RESTfulTerminalApp
from person import Person
from session import Session

@pytest.fixture
def app_instance():
    return RESTfulTerminalApp()

class TestPersonDeletion:

    def test_delete_person_success(self, app_instance):
        app_instance.app.people = {
            "alice": Person(username="alice", password="wonderland", name="Alice", status="talking to bob"),
            "bob": Person(username="bob", password="epsilon", name="Bob", status="talking to alice"),
        }
        result = app_instance.app.delete_person("alice")
        assert result == "success"
        assert "alice" not in app_instance.app.people

    def test_delete_person_not_found(self, app_instance):
        result = app_instance.app.delete_person("unknown")
        assert result == "failed to delete: user 'unknown' not found"
    
    @patch('builtins.print')
    def test_handle_delete_with_session(self, mock_print, app_instance):
        # Mock delete to return success
        app_instance.app.delete_person = MagicMock(return_value="success")
        app_instance.sessions = {"valid_token": Session("valid_token", "test_user")}
        
        # Invoke delete with a session token
        app_instance.handle_session_command("valid_token", "delete")
        
        # Assertions
        mock_print.assert_any_call("[account deleted]")
        assert "valid_token" not in app_instance.sessions

    @patch('builtins.print')
    def test_handle_delete_without_session_token(self, mock_print, app_instance):
        # Simulate delete command without a session token
        app_instance.handle_delete([])

        # Check if appropriate error message is printed
        mock_print.assert_called_with("Usage: delete <username>")

    @patch('builtins.print')
    def test_handle_delete_invalid_user(self, mock_print, app_instance):
        # Mock delete to return failure
        app_instance.app.delete_person = MagicMock(return_value="failed to delete: user 'unknown_user' not found")
        
        # Attempt to delete a non-existent user
        app_instance.handle_delete(["unknown_user"])

        # Check if error message is printed
        mock_print.assert_any_call("try harder.\nresource not found\nhome: ./app")
