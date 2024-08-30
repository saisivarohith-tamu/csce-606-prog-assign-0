#!/usr/bin/python3

# test/test_main.py
import pytest
from unittest.mock import patch, mock_open, MagicMock, call
from main import RESTfulTerminalApp
from person import Person
from session import Session
from app import Application

# Helper function to create mock Person instances
def create_mock_person(username="test_user", password="password123", name="Old Name", status="Old Status"):
    return Person(username=username, password=password, name=name, status=status, updated_at=None)

@pytest.fixture
def app_instance():
    return RESTfulTerminalApp()

# Testing instances
def test_initialization(app_instance):
    assert isinstance(app_instance, RESTfulTerminalApp)
    assert isinstance(app_instance.app, Application)
    assert app_instance.session_file == 'sessions.json'
    assert isinstance(app_instance.sessions, dict)

# Test to verify the generated session token
def test_generate_session_token(app_instance):
    token = app_instance.generate_session_token()
    assert len(token) == 16
    assert isinstance(token, str)

@patch('os.path.exists', return_value=False)
@patch('builtins.open', new_callable=mock_open)
def test_load_sessions_file_not_exist(mock_open, mock_exists, app_instance):
    sessions = app_instance.load_sessions()
    assert sessions == {}

@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='{"token123": {"token": "token123", "username": "user1"}}')
def test_load_sessions(mock_open, mock_exists, app_instance):
    sessions = app_instance.load_sessions()
    assert len(sessions) == 1
    assert "token123" in sessions
    assert isinstance(sessions["token123"], Session)

@patch('builtins.open', new_callable=mock_open)
def test_save_sessions(mock_open, app_instance):
    app_instance.sessions = {
        "token123": Session("token123", "user1")
    }
    app_instance.save_sessions()
    mock_open.assert_called_with('sessions.json', 'w')

@patch('builtins.open', new_callable=mock_open)
def test_save_sessions_os_error(mock_open, app_instance):
    mock_open.side_effect = OSError("Error creating directory")
    with pytest.raises(OSError):
        app_instance.save_sessions()

@patch.object(Application, 'authenticate_user', return_value={"name": "User One", "status": "active"})
@patch('builtins.print')
@patch.object(RESTfulTerminalApp, 'save_sessions')
def test_handle_login_success(mock_save_sessions, mock_print, mock_authenticate_user, app_instance):
    app_instance.sessions.clear()
    app_instance.handle_login(["user1", "password1"])
    assert len(app_instance.sessions) > 0
    mock_print.assert_any_call('Welcome back to the App, User One!')

def test_login_no_password(app_instance, capsys):
    # adding a user to the system for testing
    app_instance.app.people['alice1'] = Person(username='alice1', password='password', name='Alice', status='status')
    
    app_instance.handle_login(['alice1'])  # Simulate providing only username without password
    captured = capsys.readouterr()
    assert "incorrect username or password" in captured.out
    assert "home: ./app" in captured.out

@patch.object(Application, 'authenticate_user', return_value="access denied: incorrect username or password\nhome: ./app")
@patch('builtins.print')
def test_handle_login_failure(mock_print, mock_authenticate_user, app_instance):
    app_instance.handle_login(["user1", "wrong_pass"])
    mock_print.assert_called_with("access denied: incorrect username or password\nhome: ./app")

@patch.object(Application, 'create_person', return_value="success")
@patch.object(Application, 'get_person', return_value=create_mock_person())
@patch('builtins.input', side_effect=["user1", "password1", "password1", "John Smith", "inactive"])
@patch('builtins.print')
@patch.object(RESTfulTerminalApp, 'save_sessions')
def test_handle_join_success(mock_save_sessions, mock_print, mock_input, mock_get_person, mock_create_person, app_instance):
    app_instance.sessions.clear()
    app_instance.handle_join()
    assert len(app_instance.sessions) > 0
    mock_print.assert_any_call("\n[account created]")

@patch('builtins.print')
def test_handle_invalid_command(mock_print, app_instance):
    app_instance.parse_command("invalid_command")
    mock_print.assert_called_with("home: ./app")

@patch('builtins.print')
def test_handle_invalid_session(mock_print, app_instance):
    app_instance.handle_invalid_session()
    mock_print.assert_called_with("try harder.\ninvalid request: invalid session token\nhome: ./app")

@patch('builtins.print')
def test_handle_resource_not_found(mock_print, app_instance):
    app_instance.handle_resource_not_found()
    mock_print.assert_called_with("try harder.\nresource not found\nhome: ./app")

@patch('builtins.print')
def test_handle_people_no_session(mock_print, app_instance):
    app_instance.app.list_people = MagicMock(return_value=[])
    app_instance.handle_people()
    mock_print.assert_any_call("People\nNo one is here...")
    mock_print.assert_any_call("Welcome to the App!\n")

@patch('builtins.print')
def test_print_home_commands(mock_print, app_instance):
    app_instance.print_home_commands()
    mock_print.assert_any_call("login: ./app 'login <username> <password>'")
    mock_print.assert_any_call("join: ./app 'join'")
    mock_print.assert_any_call("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
    mock_print.assert_any_call("show people: ./app 'people'")

@patch('builtins.print')
def test_print_logout_commands(mock_print, app_instance):
    app_instance.print_logout_commands()
    mock_print.assert_any_call("login: ./app 'login <username> <password>'")
    mock_print.assert_any_call("join: ./app 'join'")
    mock_print.assert_any_call("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
    mock_print.assert_any_call("people: ./app 'people'")

@patch('builtins.print')
def test_print_people_commands(mock_print, app_instance):
    app_instance.print_people_commands()
    mock_print.assert_any_call("find: ./app 'find <pattern>'")
    mock_print.assert_any_call("sort: ./app 'sort[ username|name|status|updated[ asc|desc]]'")
    mock_print.assert_any_call("join: ./app 'join'")
    mock_print.assert_any_call("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
    mock_print.assert_any_call("home: ./app")

@patch('builtins.print')
def test_print_find_commands(mock_print, app_instance):
    app_instance.print_find_commands()
    mock_print.assert_any_call("find: ./app 'find <pattern>'")
    mock_print.assert_any_call("sort: ./app 'sort[ username|name|status|updated[ asc|desc]]'")
    mock_print.assert_any_call("people: ./app 'people'")
    mock_print.assert_any_call("join: ./app 'join'")
    mock_print.assert_any_call("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
    mock_print.assert_any_call("home: ./app")

@patch('builtins.print')
def test_print_post_delete_commands(mock_print, app_instance):
    app_instance.print_post_delete_commands()
    mock_print.assert_any_call("Welcome to the App!\n")
    mock_print.assert_any_call("login: ./app 'login <username> <password>'")
    mock_print.assert_any_call("join: ./app 'join'")
    mock_print.assert_any_call("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
    mock_print.assert_any_call("show people: ./app 'people'")

@patch('builtins.print')
def test_print_show_person_commands(mock_print, app_instance):
    app_instance.print_show_person_commands()
    mock_print.assert_any_call("people: ./app 'people'")
    mock_print.assert_any_call("home: ./app")

@patch('builtins.print')
def test_print_update_commands(mock_print, app_instance):
    app_instance.print_update_commands()
    mock_print.assert_any_call("show people: ./app 'people'")
    mock_print.assert_any_call("find: ./app 'find <pattern>'")
    mock_print.assert_any_call("sort: ./app 'sort <key> <order>'")

@patch('builtins.print')
def test_print_delete_commands(mock_print, app_instance):
    app_instance.print_delete_commands()
    mock_print.assert_any_call("show people: ./app 'people'")
    mock_print.assert_any_call("find: ./app 'find <pattern>'")
    mock_print.assert_any_call("sort: ./app 'sort <key> <order>'")

@patch('builtins.input', side_effect=["invalid command", "exit"])
@patch('builtins.print')
def test_run_with_invalid_command(mock_print, mock_input, app_instance):
    app_instance.run()
    mock_print.assert_any_call("home: ./app")
    mock_print.assert_any_call("Welcome to the App!")

def test_initialization_no_session_file():
    with patch('os.path.exists', return_value=False), \
         patch('builtins.open', new_callable=mock_open):
        app = RESTfulTerminalApp()
        assert app.sessions == {}

@patch.object(Application, 'get_person', return_value=Person(username="test_user", password="password123", name="prof. ritchey", status="Active"))
@patch('builtins.print')
def test_handle_session_command_home(mock_print, mock_get_person, app_instance):
    app_instance.sessions = {"test_token": Session("test_token", "test_user")}
    app_instance.handle_session_command("test_token", "home")
    mock_print.assert_any_call("Welcome back to the App, prof. ritchey!\n")
    mock_print.assert_any_call('"Active"\n')

def test_handle_invalid_command_unrecognized(app_instance):
    with patch('builtins.print') as mock_print:
        app_instance.parse_command("unrecognized_command")
        mock_print.assert_called_with("home: ./app")

@patch.object(Application, 'sort_people', return_value=[])
@patch('builtins.print')
def test_handle_sort_no_results(mock_print, mock_sort_people, app_instance):
    app_instance.handle_sort(['username', 'asc'])
    mock_print.assert_any_call("try harder.\nresource not found\nhome: ./app")

@patch('builtins.print')
def test_parse_command_invalid(mock_print, app_instance):
    app_instance.parse_command("invalid_command")
    mock_print.assert_called_with("home: ./app")

@patch('builtins.print')
def test_parse_command_missing_argument(mock_print, app_instance):
    app_instance.parse_command("login")
    mock_print.assert_called_with("invalid request: missing username and password\nhome: ./app")

@patch('builtins.print')
def test_handle_session_command_invalid_subcommand(mock_print, app_instance):
    app_instance.sessions = {"valid_token": Session("valid_token", "test_user")}
    app_instance.handle_session_command("valid_token", "unknown_command")
    mock_print.assert_called_with("Invalid session command: unknown_command")

@patch('builtins.print')
def test_handle_show_no_args(mock_print, app_instance):
    app_instance.handle_show([])
    mock_print.assert_called_once_with("invalid request: missing username\nhome: ./app")

@patch.object(Application, 'get_person', return_value=None)
@patch('builtins.print')
def test_handle_show_invalid_user(mock_print, mock_get_person, app_instance):
    app_instance.sessions = {"valid_token": Session("valid_token", "test_user")}
    app_instance.handle_show(["valid_token", "non_existent_user"])
    mock_print.assert_called_with("try harder.\nresource not found\nhome: ./app")

@patch('builtins.print')
def test_parse_command_with_partial_arguments(mock_print, app_instance):
    app_instance.parse_command("session token")
    mock_print.assert_called_with("try harder.\ninvalid request: invalid session token\nhome: ./app")

@patch('builtins.print')
def test_parse_command_session_command_missing_token(mock_print, app_instance):
    app_instance.parse_command("session")
    mock_print.assert_called_with("Invalid session command.")

@patch('os.makedirs', side_effect=OSError("Cannot create directory"))
@patch('builtins.open', new_callable=mock_open)
@patch('builtins.print')
def test_save_sessions_directory_creation_error(mock_print, mock_open, mock_makedirs, app_instance):
    app_instance.session_file = "/non/existent/directory/sessions.json"
    with pytest.raises(OSError):
        app_instance.save_sessions()
    mock_print.assert_any_call("Error creating directory /non/existent/directory: Cannot create directory")

@patch('builtins.print')
def test_parse_command_home_with_extra_args(mock_print, app_instance):
    app_instance.parse_command("home extra_arg")
    mock_print.assert_called_with("home: ./app")

@patch('builtins.print')
def test_logout_session_command(mock_print, app_instance):
    app_instance.sessions = {"valid_token": Session("valid_token", "test_user")}
    app_instance.handle_session_command("valid_token", "logout")
    mock_print.assert_any_call("[you are now logged out]")  # Use assert_any_call to check if the message was printed at any point

@patch('builtins.print')
def test_logout_session_command(mock_print, app_instance):
    token = app_instance.generate_session_token()
    app_instance.sessions[token] = Session(token, "test_user")
    app_instance.parse_command(f"session {token} logout")
    mock_print.assert_any_call("[you are now logged out]")
    assert token not in app_instance.sessions  # Check that the session was deleted

def test_logout_without_session_token(app_instance, capsys):
    app_instance.handle_session_command("", "logout")  # Simulate logout without session token
    captured = capsys.readouterr()
    assert "invalid request: missing session token" in captured.out
    assert "home: ./app" in captured.out

@patch('builtins.print')
def test_find_invalid_attribute(mock_print, app_instance):
    app_instance.parse_command("find username2: pcr")
    mock_print.assert_any_call("try harder.\nresource not found\nhome: ./app")

@patch('builtins.print')
def test_print_person_info_dict(mock_print, app_instance):
    # Setup a person dictionary
    person_dict = {
        'name': 'Old Name',
        'username': 'pcr',
        'status': 'Active',
        'updated_at': '2024-08-25 19:32:55'
    }
    
    # Call the method with the dictionary
    app_instance.print_person_info(person_dict)

    # Assertions
    mock_print.assert_any_call("Person\n------")
    mock_print.assert_any_call("name: Old Name")
    mock_print.assert_any_call("username: pcr")
    mock_print.assert_any_call("status: Active")
    mock_print.assert_any_call("updated: 2024-08-25 19:32:55")

@patch('builtins.print')
def test_print_sort_commands(mock_print, app_instance):
    app_instance.print_sort_commands()
    
    # Create the expected output using call()
    expected_calls = [
        call("\n"),
        call("find: ./app 'find <pattern>'"),
        call("sort: ./app 'sort[ username|name|status|updated[ asc|desc]]'"),
        call("people: ./app 'people'"),
        call("join: ./app 'join'"),
        call('create: ./app \'create username="<value>" password="<value>" name="<value>" status="<value>"\''),
        call('home: ./app')
    ]
    
    # Check if all expected calls were made in order
    mock_print.assert_has_calls(expected_calls, any_order=False)

@patch('builtins.print')
@patch.object(RESTfulTerminalApp, 'handle_invalid_session')
def test_handle_people_with_valid_session_and_people(mock_invalid_session, mock_print, app_instance):
    # Mock the session and person objects
    session_token = "valid_token"
    username = "test_user"
    mock_session = Session(token=session_token, username=username)
    mock_person = Person(username=username, password="password", name="Test User", status="Active", updated_at=None)
    
    # Set up the mock environment
    app_instance.sessions = {session_token: mock_session}
    app_instance.app.get_person = MagicMock(return_value=mock_person)
    app_instance.app.list_people = MagicMock(return_value=[
        {'name': 'John Doe', 'username': 'jdoe', 'status': 'Online', 'updated_at': '2024-08-26 11:15:07'}
    ])

    # Call the method
    app_instance.handle_people(session_token)

    # Assert that handle_invalid_session was not called
    mock_invalid_session.assert_not_called()

    # Check that the people info was printed correctly
    mock_print.assert_any_call("People\n------")
    mock_print.assert_any_call("John Doe @jdoe (./app 'show jdoe')")
    mock_print.assert_any_call("Online")
    mock_print.assert_any_call("@ 2024-08-26 11:15:07")

@patch('builtins.print')
@patch.object(RESTfulTerminalApp, 'handle_invalid_session')
def test_handle_people_with_valid_session_but_no_people(mock_invalid_session, mock_print, app_instance):
    # Mock the session object
    session_token = "valid_token"
    username = "test_user"
    mock_session = Session(token=session_token, username=username)
    
    # Set up the mock environment
    app_instance.sessions = {session_token: mock_session}
    app_instance.app.get_person = MagicMock(return_value=mock_session)
    app_instance.app.list_people = MagicMock(return_value=[])

    # Call the method
    app_instance.handle_people(session_token)

    # Assert that handle_invalid_session was not called
    mock_invalid_session.assert_not_called()

    # Check that no people registered message was printed
    mock_print.assert_any_call("People\nNo one is here...")
    mock_print.assert_any_call("Welcome to the App!\n")

@patch('builtins.print')
@patch.object(RESTfulTerminalApp, 'handle_invalid_session')
def test_handle_people_with_invalid_session(mock_invalid_session, mock_print, app_instance):
    # Call the method with a session token that is not in app_instance.sessions
    invalid_session_token = "invalid_token"
    
    # Ensure no valid session is present
    app_instance.sessions = {}  # No sessions exist

    app_instance.handle_people(invalid_session_token)

    # Assert that handle_invalid_session was called
    mock_invalid_session.assert_called_once()

@patch('builtins.print')
def test_handle_people_no_session_token_with_people(mock_print, app_instance):
    # Mock the list_people method to return some people
    app_instance.app.list_people = MagicMock(return_value=[
        {'name': 'John Doe', 'username': 'jdoe', 'status': 'Online', 'updated_at': '2024-08-26 11:15:07'}
    ])

    # Call the method without a session token
    app_instance.handle_people()

    # Check that the people info was printed correctly
    mock_print.assert_any_call("People\n------")
    mock_print.assert_any_call("John Doe @jdoe (./app 'show jdoe')")
    mock_print.assert_any_call("Online")
    mock_print.assert_any_call("@ 2024-08-26 11:15:07")

@patch('builtins.print')
def test_handle_people_no_session_token_no_people(mock_print, app_instance):
    # Mock the list_people method to return no people
    app_instance.app.list_people = MagicMock(return_value=[])

    # Call the method without a session token
    app_instance.handle_people()

    # Check that no people registered message was printed
    mock_print.assert_any_call("People\nNo one is here...")
    mock_print.assert_any_call("Welcome to the App!\n")

@patch('builtins.print')
def test_sort_invalid_order(mock_print, app_instance):
    # Test sorting with an invalid order
    app_instance.handle_sort(['username', 'bogo'])
    
    # Assert that handle_resource_not_found was called
    mock_print.assert_any_call("try harder.\nresource not found\nhome: ./app")

@patch.object(RESTfulTerminalApp, 'print_sort_commands')
@patch('builtins.print')
def test_handle_sort_by_name_ascending(mock_print, mock_print_sort_commands, app_instance):
    sorted_people = [
        {'name': 'Alice', 'username': 'alice123', 'status': 'Active', 'updated_at': '2024-08-26 11:15:07'},
        {'name': 'Bob', 'username': 'bob456', 'status': 'Inactive', 'updated_at': '2024-08-26 12:00:00'}
    ]
    app_instance.app.sort_people = MagicMock(return_value=sorted_people)
    
    app_instance.handle_sort(['name', 'asc'])

    mock_print.assert_any_call("People (sorted by name, a-z)\n----------------------------")
    mock_print.assert_any_call("Alice @alice123 (./app 'show alice123')")
    mock_print.assert_any_call("Active")
    mock_print.assert_any_call("@ 2024-08-26 11:15:07")
    mock_print.assert_any_call("Bob @bob456 (./app 'show bob456')")
    mock_print.assert_any_call("Inactive")
    mock_print.assert_any_call("@ 2024-08-26 12:00:00")
    mock_print_sort_commands.assert_called_once()

@patch.object(RESTfulTerminalApp, 'print_sort_commands')
@patch('builtins.print')
def test_handle_sort_by_name_descending(mock_print, mock_print_sort_commands, app_instance):
    sorted_people = [
        {'name': 'Bob', 'username': 'bob456', 'status': 'Inactive', 'updated_at': '2024-08-26 12:00:00'},
        {'name': 'Alice', 'username': 'alice123', 'status': 'Active', 'updated_at': '2024-08-26 11:15:07'}
    ]
    app_instance.app.sort_people = MagicMock(return_value=sorted_people)
    
    app_instance.handle_sort(['name', 'desc'])

    mock_print.assert_any_call("People (sorted by name, z-a)\n----------------------------")
    mock_print.assert_any_call("Bob @bob456 (./app 'show bob456')")
    mock_print.assert_any_call("Inactive")
    mock_print.assert_any_call("@ 2024-08-26 12:00:00")
    mock_print.assert_any_call("Alice @alice123 (./app 'show alice123')")
    mock_print.assert_any_call("Active")
    mock_print.assert_any_call("@ 2024-08-26 11:15:07")
    mock_print_sort_commands.assert_called_once()

@patch.object(RESTfulTerminalApp, 'print_sort_commands')
@patch('builtins.print')
def test_handle_sort_by_username_ascending(mock_print, mock_print_sort_commands, app_instance):
    sorted_people = [
        {'name': 'Charlie', 'username': 'charlie123', 'status': 'Active', 'updated_at': '2024-08-26 09:00:00'},
        {'name': 'David', 'username': 'david456', 'status': 'Inactive', 'updated_at': '2024-08-26 10:30:00'}
    ]
    app_instance.app.sort_people = MagicMock(return_value=sorted_people)
    
    app_instance.handle_sort(['username', 'asc'])

    mock_print.assert_any_call("People (sorted by username, a-z)\n----------------------------")
    mock_print.assert_any_call("Charlie @charlie123 (./app 'show charlie123')")
    mock_print.assert_any_call("Active")
    mock_print.assert_any_call("@ 2024-08-26 09:00:00")
    mock_print.assert_any_call("David @david456 (./app 'show david456')")
    mock_print.assert_any_call("Inactive")
    mock_print.assert_any_call("@ 2024-08-26 10:30:00")
    mock_print_sort_commands.assert_called_once()

@patch.object(RESTfulTerminalApp, 'print_sort_commands')
@patch('builtins.print')
def test_handle_sort_by_status_descending(mock_print, mock_print_sort_commands, app_instance):
    sorted_people = [
        {'name': 'Eve', 'username': 'eve123', 'status': 'Online', 'updated_at': '2024-08-26 08:15:00'},
        {'name': 'Frank', 'username': 'frank456', 'status': 'Offline', 'updated_at': '2024-08-26 07:45:00'}
    ]
    app_instance.app.sort_people = MagicMock(return_value=sorted_people)
    
    app_instance.handle_sort(['status', 'desc'])

    mock_print.assert_any_call("People (sorted by status, z-a)\n----------------------------")
    mock_print.assert_any_call("Eve @eve123 (./app 'show eve123')")
    mock_print.assert_any_call("Online")
    mock_print.assert_any_call("@ 2024-08-26 08:15:00")
    mock_print.assert_any_call("Frank @frank456 (./app 'show frank456')")
    mock_print.assert_any_call("Offline")
    mock_print.assert_any_call("@ 2024-08-26 07:45:00")
    mock_print_sort_commands.assert_called_once()

@patch('builtins.print')
def test_handle_sort_invalid_key(mock_print, app_instance):
    app_instance.app.sort_people = MagicMock(return_value=[])
    
    app_instance.handle_sort(['invalid_key'])

    mock_print.assert_any_call("try harder.\nresource not found\nhome: ./app")

@pytest.mark.parametrize(
    "input_side_effect, expected_print_calls",
    [
        (["New Name", ""], ["\n[name updated]"]),  # Only name updated
        (["", "New Status"], ["\n[status updated]"]),  # Only status updated
        (["New Name", "New Status"], ["\n[name and status updated]"]),  # Both updated
        (["", ""], [])  # No changes made
    ]
)
@patch.object(Application, 'get_person', return_value=create_mock_person())
@patch('builtins.input')
@patch('builtins.print')
def test_handle_edit_consolidated(mock_print, mock_input, mock_get_person, app_instance, input_side_effect, expected_print_calls):
    # Setup the input side effects and session
    mock_input.side_effect = input_side_effect
    app_instance.sessions = {"valid_token": Session("valid_token", "test_user")}
    
    # Invoke the method
    app_instance.handle_edit(['valid_token'])
    
    # Assert that the expected print calls were made
    for expected_call in expected_print_calls:
        mock_print.assert_any_call(expected_call)
    
    # Always check that person info is printed at the end
    mock_print.assert_any_call("Person\n------")
    mock_print.assert_any_call("username: test_user")

@pytest.mark.parametrize(
    "update_args, expected_print_calls",
    [
        (['name="Updated Name"'], ["[name updated]", "name: Updated Name"]),  # Only name updated
        (['status="Updated Status"'], ["[status updated]", "status: Updated Status"]),  # Only status updated
        (['name="Updated Name"', 'status="Updated Status"'], ["[name and status updated]", "name: Updated Name", "status: Updated Status"]),  # Both updated
        ([], ["Usage: update (name=\"<value>\"|status=\"<value>\")"])  # Invalid command usage
    ]
)
@patch.object(Application, 'update_person', return_value="success")
@patch.object(Application, 'get_person', side_effect=lambda username: create_mock_person(name="Updated Name", status="Updated Status"))
@patch('builtins.print')
@patch.object(RESTfulTerminalApp, 'save_sessions')
def test_handle_update_consolidated(mock_save_sessions, mock_print, mock_get_person, mock_update_person, app_instance, update_args, expected_print_calls):
    # Setup the session
    session_token = "token123"
    app_instance.sessions = {session_token: Session(session_token, "test_user")}
    
    # Create the command for handle_session_command
    command = ' '.join(['update'] + update_args)
    
    # Invoke the handle_session_command method
    app_instance.handle_session_command(session_token, command)
    
    # Assert that the expected print calls were made
    for expected_call in expected_print_calls:
        mock_print.assert_any_call(expected_call)
    
    # Check that the person info is printed at the end
    if "Usage" not in expected_print_calls[0]:
        mock_print.assert_any_call("Person\n------")
        if "name: Updated Name" in expected_print_calls:
            mock_print.assert_any_call("name: Updated Name")
        if "status: Updated Status" in expected_print_calls:
            mock_print.assert_any_call("status: Updated Status")

@patch('builtins.print')
def test_update_without_session_id(mock_print, app_instance):
    # Simulate the update command without a session ID
    app_instance.parse_command('update name="prof. ritchey updated" status="feeling updated"')
    
    # Assert that the expected error message is printed
    mock_print.assert_any_call("try harder.\ninvalid request: invalid session token\nhome: ./app")

@patch('builtins.print')
def test_handle_edit_invalid_args(mock_print, app_instance):
    # Test with no arguments
    app_instance.handle_edit([])
    mock_print.assert_called_with("Usage: edit <session token>")

    # Test with more than one argument
    app_instance.handle_edit(['token1', 'token2'])
    mock_print.assert_called_with("Usage: edit <session token>")
