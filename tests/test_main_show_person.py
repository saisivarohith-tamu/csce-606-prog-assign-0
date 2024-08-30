import pytest
from unittest.mock import patch
from main import RESTfulTerminalApp
from person import Person
from session import Session

@pytest.fixture
def app_instance():
    return RESTfulTerminalApp()

class TestShowUserProfile:

    @patch('builtins.print')
    def test_show_own_profile_with_session(self, mock_print, app_instance):
        
        session_token = "test_token"
        username = "alice"
        
        # Mocking session and person
        app_instance.sessions = {session_token: Session(token=session_token, username=username)}
        person_info = Person(username=username, password="password", name="Alice", status="i <3 bob")
        app_instance.app.get_person = lambda x: person_info if x == username else None
        
        # Run the command
        app_instance.handle_show([session_token, username])
        
        # Check output
        mock_print.assert_any_call("name: Alice")
        mock_print.assert_any_call("username: alice")
        mock_print.assert_any_call("status: i <3 bob")
        mock_print.assert_any_call(f"edit: ./app 'session {session_token} edit'")
        mock_print.assert_any_call(f"update: ./app 'session {session_token} update (name=\"<value>\"|status=\"<value>\")+'")
        mock_print.assert_any_call(f"delete: ./app 'session {session_token} delete'")

    @patch('builtins.print')
    def test_show_another_user_profile_with_session(self, mock_print, app_instance):
        session_token = "test_token"
        session_username = "alice"
        another_username = "bob"
        
        # Mocking session and person
        app_instance.sessions = {session_token: Session(token=session_token, username=session_username)}
        another_person_info = Person(username=another_username, password="password", name="Bob", status="talking to alice")
        app_instance.app.get_person = lambda x: another_person_info if x == another_username else None
        
        # Run the command
        app_instance.handle_show([session_token, another_username])
        
        # Check output
        mock_print.assert_any_call("name: Bob")
        mock_print.assert_any_call("username: bob")
        mock_print.assert_any_call("status: talking to alice")
        
        # Ensure no edit, update, delete commands are shown
        assert not any("edit: ./app" in call[0][0] for call in mock_print.call_args_list)
        assert not any("update: ./app" in call[0][0] for call in mock_print.call_args_list)
        assert not any("delete: ./app" in call[0][0] for call in mock_print.call_args_list)
        
        # Check that only basic commands are shown
        mock_print.assert_any_call(f"logout: ./app 'session {session_token} logout'")
        mock_print.assert_any_call(f"people: ./app '[session {session_token} ]people'")
        mock_print.assert_any_call(f"home: ./app ['session {session_token}']")