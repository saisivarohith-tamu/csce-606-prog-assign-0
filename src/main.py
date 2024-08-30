#!/usr/bin/python3

# src/main.py
import sys
import json
import os
import random
import string
from app import Application
from person import Person
from session import Session

class RESTfulTerminalApp:

    def __init__(self, session_file='sessions.json'):
        self.app = Application()
        self.session_file = session_file
        self.sessions = self.load_sessions()

    def generate_session_token(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def load_sessions(self):
        if not os.path.exists(self.session_file):
            return {}
        try:
            with open(self.session_file, 'r') as file:
                session_data = json.load(file)
                return {token: Session.from_dict(session_info) for token, session_info in session_data.items()}
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as e:
            print(f"Error loading sessions file: {e}")
            raise  # re-raise the caught exception

    def save_sessions(self):
        try:
            directory = os.path.dirname(self.session_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            with open(self.session_file, 'w') as file:
                session_data = {token: session.to_dict() for token, session in self.sessions.items()}
                json.dump(session_data, file)
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")
            raise
        except Exception as e:
            print(f"Error saving sessions: {e}")
            raise

    def run(self, command=None):
        if command:
            self.parse_command(command)
        else:
            print("Welcome to the App!")
            print("")
            while True:
                command = input("Enter command: ").strip()
                if command.lower() in ['exit', 'quit']:
                    break
                self.parse_command(command)

    # parse the given command
    def parse_command(self, command):
        if command.startswith("./app"):
            command = command[7:].strip("'")
        parts = command.split()
        # parse session commands
        if parts[0] == 'session':
            if len(parts) < 2:
                print("Invalid session command.")
                return
            session_token = parts[1].strip()
            if len(parts) == 2:
                self.handle_session_command(session_token, 'home')
            else:
                if session_token not in self.sessions:
                    self.handle_invalid_session()
                    return

                command_parts = parts[2:]
                command = ' '.join(command_parts)
                self.handle_session_command(session_token, command)
        # parse direct commands
        else:
            if parts[0] == 'login':
                self.handle_login(parts[1:])
            elif parts[0] == 'join':
                self.handle_join()
            elif parts[0] == 'create':
                self.handle_create(parts[1:])
            elif parts[0] == 'people':
                self.handle_people(parts[1:])
            elif parts[0] == 'find':
                self.handle_find(parts[1:])
            elif parts[0] == 'sort':
                self.handle_sort(parts[1:])
            elif parts[0] == 'home':
                self.handle_home(parts[1:])
            elif parts[0] == 'show':
                self.handle_show(parts[1:])
            elif parts[0] == 'edit':
                self.handle_edit(parts[1:])
            elif parts[0] == 'update':
                self.handle_update(parts[1:])
            elif parts[0] == 'delete':
                self.handle_delete(parts[1:])
            else:
                print("home: ./app")

    def handle_invalid_session(self):
        print("try harder.\ninvalid request: invalid session token\nhome: ./app")

    def handle_resource_not_found(self):
        print("try harder.\nresource not found\nhome: ./app")

    def handle_login(self, args):
        if len(args) == 0:
            print("invalid request: missing username and password\nhome: ./app")
            return
        elif len(args) == 1:
            print("incorrect username or password\nhome: ./app")
            return

        username, password = args
        person = self.app.authenticate_user(username, password)

        if isinstance(person, dict):
            token = self.generate_session_token()
            self.sessions[token] = Session(token, username)
            print(f"Welcome back to the App, {person['name']}!")
            print(f'"{person["status"]}"')
            self.save_sessions()
            self.print_session_commands(token)
        else:
            print(person)

    # handle all session commands
    def handle_session_command(self, session_token, command):
        if not session_token:  # Check if session token is missing
            print("invalid request: missing session token")
            print("home: ./app")
            return

        if session_token not in self.sessions:
            self.handle_invalid_session()
            return

        username = self.sessions[session_token].username

        if command == 'home':
            self.print_session_home(username, session_token)
            return

        parts = command.split()
        subcommand = parts[0].lower()
        args = parts[1:]

        if subcommand == 'update':
            if 'name' in command or 'status' in command:
                self.handle_update([session_token] + args)
            else:
                print("Usage: update (name=\"<value>\"|status=\"<value>\")")
        elif subcommand == 'people':
            self.handle_people(session_token=session_token)
        elif subcommand == 'join':
            print("You are already logged in. Log out first to join as a different user.")
        elif subcommand == 'home':
            self.print_session_home(username, session_token)
        elif subcommand == 'edit':
            self.handle_edit([session_token])
        elif subcommand == 'logout':
            print("[you are now logged out]")
            del self.sessions[session_token]
            self.save_sessions()
            self.print_logout_commands()
        elif subcommand == 'show':
            self.handle_show([session_token] + args)
        elif subcommand == 'delete':
            if session_token in self.sessions:
                username = self.sessions[session_token].username
                result = self.app.delete_person(username)
                if result == "success":
                    del self.sessions[session_token]
                    self.save_sessions()
                    print("[account deleted]")
                    self.print_post_delete_commands()
                else:
                    self.handle_resource_not_found()
            else:
                self.handle_invalid_session()
        else:
            print(f"Invalid session command: {subcommand}")

    def print_home_commands(self):
        print("Welcome to the App!\n")
        print("login: ./app 'login <username> <password>'")
        print("join: ./app 'join'")
        print("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
        print("show people: ./app 'people'")

    def handle_join(self):
        print("New Person\n----------")
        username = input("username: ").strip()
        password = input("password: ").strip()
        confirm_password = input("confirm password: ").strip()
        name = input("name: ").strip()
        status = input("status: ").strip()

        if password != confirm_password:
            print("\ntry harder.\nfailed to join: passwords do not match\nhome: ./app")
            return

        result = self.app.create_person(username, password, name, status)

        if result == "success":
            token = self.generate_session_token()
            self.sessions[token] = Session(token, username)
            self.save_sessions()
            person = self.app.get_person(username)
            if isinstance(person, Person):
                print(f"\n[account created]")
                self.print_person_info(person)
                self.print_join_session_commands(token)
            else:
                print("Error retrieving person information.")
        else:
            print(f"try harder.\n{result}\nhome: ./app")

    def handle_create(self, args):
        arg_dict = self.parse_key_value_args(args)
        required_keys = {'username', 'password', 'name', 'status'}
        missing_keys = required_keys - arg_dict.keys()
        
        if missing_keys:
            for missing in missing_keys:
                reason = f"missing {missing}"
                print(f"try harder.\nfailed to create: {reason}\nhome: ./app")
            return

        result = self.app.create_person(**arg_dict)
        if result == "success":
            print(f"[account created]\n")
            token = self.generate_session_token()
            self.sessions[token] = Session(token, arg_dict['username'])
            self.save_sessions()
            self.print_person_info(self.app.get_person(arg_dict['username']))
            self.print_create_session_commands(token)
        else:
            print(f"try harder.\n{result}\nhome: ./app")

    def handle_update(self, args):
        if len(args) < 2:
            print("invalid request: missing session token\n")
            print("Usage: session <token> update (name=\"<value>\"|status=\"<value>\")")
            return

        session_token = args[0]
        session = self.sessions.get(session_token)
        if not session:
            self.handle_invalid_session()
            return

        username = session.username
        update_data = self.parse_key_value_args(args[1:])
        result = self.app.update_person(username, **update_data)

        if result == "success":
            if 'name' in update_data and 'status' in update_data:
                print("[name and status updated]")
            elif 'name' in update_data:
                print("[name updated]")
            elif 'status' in update_data:
                print("[status updated]")

            self.print_person_info(self.app.get_person(username))
            self.print_show_person_session_commands(session_token)
        else:
            print(result)

    # function to parse key-value pairs
    def parse_key_value_args(self, args):
        arg_dict = {}
        key = None
        value = []

        for arg in args:
            if '=' in arg:
                if key:
                    arg_dict[key] = ' '.join(value).strip('"')
                key, value = arg.split('=', 1)
                key = key.strip()
                value = [value.strip()]
            else:
                value.append(arg.strip())

        if key:
            arg_dict[key] = ' '.join(value).strip('"')

        return arg_dict

    def print_person_info(self, person):
        if isinstance(person, Person):
            print(f"Person\n------")
            print(f"name: {person.name}")
            print(f"username: {person.username}")
            print(f"status: {person.status}")
            print(f"updated: {person.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        elif isinstance(person, dict):
            print(f"Person\n------")
            print(f"name: {person['name']}")
            print(f"username: {person['username']}")
            print(f"status: {person['status']}")
            print(f"updated: {person['updated_at']}")
        else:
            print("Invalid person information.")

    def handle_people(self, session_token=None):
        if session_token:
            if session_token not in self.sessions:
                self.handle_invalid_session()
                return
            
            session = self.sessions.get(session_token)
            if not session:
                self.handle_invalid_session()
                return

            username = session.username
            person = self.app.get_person(username)
        else:
            session_token = None

        people = self.app.list_people()
        if people:
            print("People\n------")
            for person in people:
                print(f"{person['name']} @{person['username']} (./app 'show {person['username']}')")
                print(f"{person['status']}")
                print(f"@ {person['updated_at']}")
            if session_token:
                self.print_people_session_commands(session_token)
            else:
                self.print_people_commands()
        else:
            print("People\nNo one is here...")
            self.print_home_commands()

    def handle_find(self, args):
        pattern = ' '.join(args)
        
        # Extract attribute and value if they are separated by ':'
        if ':' in pattern:
            attribute, value = map(str.strip, pattern.split(':', 1))
            if attribute not in ['username', 'name', 'status', 'updated']:
                self.handle_resource_not_found()
                return
            search_pattern = f'{attribute}: {value}'
        else:
            search_pattern = pattern

        results, message = self.app.find_people(search_pattern, return_message=True)

        if results:
            print(message)
            print("----------------------------")
            for person in results:
                print(f"{person.name} @{person.username} (./app 'show {person.username}')")
                print(f"{person.status}")
                print(f"@ {person.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            self.print_find_commands()
        else:
            self.handle_resource_not_found()

    def handle_sort(self, args):
        sort_params = ' '.join(args).split()
        key = 'updated'
        order = 'desc'

        if sort_params:
            key = sort_params[0]
            if len(sort_params) > 1:
                order = sort_params[1]
                # Validating order
                if order not in {"asc", "desc"}:
                    self.handle_resource_not_found()
                    return
            else:
                if key != 'updated':
                    order = 'asc'

        sorted_people = self.app.sort_people(key, order)
        if not sorted_people and key not in ['name', 'username', 'status', 'updated']:
            self.handle_resource_not_found()
        elif sorted_people:
            # Special case handling for updated field
            if key == 'updated' and order == 'desc':
                order_display = "newest"
            elif key == 'updated' and order == 'asc':
                order_display = "oldest"
            else:
                order_display = "a-z" if order == 'asc' else "z-a"
            print(f"People (sorted by {key}, {order_display})\n----------------------------")
            for person in sorted_people:
                print(f"{person['name']} @{person['username']} (./app 'show {person['username']}')")
                print(f"{person['status']}")
                print(f"@ {person['updated_at']}")
            self.print_sort_commands()
        else:
            self.handle_resource_not_found()

    def handle_home(self, args):
        if args:
            print("home: ./app")
            return

        self.print_home_commands()

    def handle_show(self, args):
        if len(args) == 0:
            print("invalid request: missing username\nhome: ./app")
            return
        session_token = args[0]
        if session_token not in self.sessions:
            username_to_show = session_token
        else:
            username_to_show = args[1] if len(args) > 1 else None

        if not username_to_show:
            print("invalid request: missing username")
            return

        # Fetch the person to show
        person = self.app.get_person(username_to_show)
        if not person:
            self.handle_resource_not_found()
            return

        # Display the person's information
        self.print_person_info(person)

        # Determine if the session user is the same as the user being viewed
        if session_token not in self.sessions:
                self.print_basic_session_commands(session_token)
        else:
            session_username = self.sessions[session_token].username
            if session_username == username_to_show:
                self.print_show_person_session_commands(session_token)  # Show edit, update, delete commands
            else:
                self.print_basic_session_commands(session_token)  # Show only basic commands like logout, people, home

    def handle_edit(self, args):
        if len(args) != 1:
            print("Usage: edit <session token>")
            return

        session_token = args[0]
        session = self.sessions.get(session_token)
        if not session:
            self.handle_invalid_session()
            return

        username = session.username
        person = self.app.get_person(username)

        if isinstance(person, Person):
            print("Edit Person\n-----------")
            print("leave blank to keep [current value]")
            new_name = input(f"name [{person.name}]: ").strip()
            new_status = input(f"status [{person.status}]: ").strip()

            update_data = {}
            if new_name:
                update_data['name'] = new_name
            if new_status:
                update_data['status'] = new_status

            if update_data:
                person.update(**update_data)
                self.app.save_people()
                if 'name' in update_data and 'status' in update_data:
                    print("\n[name and status updated]")
                elif 'name' in update_data:
                    print("\n[name updated]")
                elif 'status' in update_data:
                    print("\n[status updated]")

            self.print_person_info(person)
            self.print_edit_session_commands(session_token)
        else:
            print(f"User '{username}' not found.")

    def handle_delete(self, args):
        if len(args) != 1:
            print("Usage: delete <username>")
            return
        username = args[0]
        result = self.app.delete_person(username)
        if result == "success":
            print(f"Person {username} deleted.")
            self.print_delete_commands()
        else:
            self.handle_resource_not_found()

    def print_basic_session_commands(self, token):
        print("\n")
        print(f"logout: ./app 'session {token} logout'")
        print(f"people: ./app '[session {token} ]people'")
        print(f"home: ./app ['session {token}']")

    def print_session_commands(self, token):
        print(f"\n")
        print(f"edit: ./app 'session {token} edit'")
        print(f"update: ./app 'session {token} update (name=\"<value>\"|status=\"<value>\")+'")
        print(f"logout: ./app 'logout {token}'")
        print(f"people: ./app '[session {token} ]people'")

    def print_join_session_commands(self, token):
        print(f"\n")
        print(f"edit: ./app 'session {token} edit'")
        print(f"update: ./app 'session {token} update (name=\"<value>\"|status=\"<value>\")+'")
        print(f"delete: ./app 'session {token} delete'")
        print(f"logout: ./app 'logout {token}'")
        print(f"show people: ./app '[session {token} ]people'")
        print(f"home: ./app ['session {token}']")

    def print_create_session_commands(self, token):
        print(f"\n")
        print(f"edit: ./app 'session {token} edit'")
        print(f"update: ./app 'session {token} update (name=\"<value>\"|status=\"<value>\")+'")
        print(f"delete: ./app 'session {token} delete'")
        print(f"logout: ./app 'logout {token}'")
        print(f"people: ./app '[session {token} ]people'")
        print(f"home: ./app ['session {token}']")

    def print_people_session_commands(self, token):
        print("\n")
        print("find: ./app 'find <pattern>'")
        print(f"edit: ./app 'session {token} edit'")
        print("sort: ./app 'sort[ username|name|status|updated[ asc|desc]]'")
        print(f"update: ./app 'session {token} update (name=\"<value>\"|status=\"<value>\")+'")
        print(f"home: ./app ['session {token}']")

    def print_people_commands(self):
        print("\n")
        print("find: ./app 'find <pattern>'")
        print("sort: ./app 'sort[ username|name|status|updated[ asc|desc]]'")
        print("join: ./app 'join'")
        print("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
        print("home: ./app")

    def print_find_commands(self):
        print("\n")
        print("find: ./app 'find <pattern>'")
        print("sort: ./app 'sort[ username|name|status|updated[ asc|desc]]'")
        print("people: ./app 'people'")
        print("join: ./app 'join'")
        print("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
        print("home: ./app")

    def print_sort_commands(self):
        print("\n")
        print("find: ./app 'find <pattern>'")
        print("sort: ./app 'sort[ username|name|status|updated[ asc|desc]]'")
        print("people: ./app 'people'")
        print("join: ./app 'join'")
        print("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
        print("home: ./app")

    def print_show_person_commands(self):
        print("\n")
        print("people: ./app 'people'")
        print("home: ./app")

    def print_show_person_session_commands(self, token):
        print("\n")
        print(f"edit: ./app 'session {token} edit'")
        print(f"update: ./app 'session {token} update (name=\"<value>\"|status=\"<value>\")+'")
        print(f"delete: ./app 'session {token} delete'")
        print(f"logout: ./app 'session {token} logout'")
        print(f"people: ./app '[session {token} ]people'")
        print(f"home: ./app ['session {token}']")

    def print_edit_session_commands(self, token):
        print("\n")
        print(f"edit: ./app 'session {token} edit'")
        print(f"update: ./app 'session {token} update (name=\"<value>\"|status=\"<value>\")+'")
        print(f"delete: ./app 'session {token} delete'")
        print(f"logout: ./app 'session {token} logout'")
        print(f"show people: ./app '[session {token} ]people'")
        print(f"home: ./app ['session {token}']")

    def print_update_commands(self):
        print("\n")
        print("show people: ./app 'people'")
        print("find: ./app 'find <pattern>'")
        print("sort: ./app 'sort <key> <order>'")

    def print_delete_commands(self):
        print("\n")
        print("show people: ./app 'people'")
        print("find: ./app 'find <pattern>'")
        print("sort: ./app 'sort <key> <order>'")

    def print_post_delete_commands(self):
        print("Welcome to the App!\n")
        print("login: ./app 'login <username> <password>'")
        print("join: ./app 'join'")
        print("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
        print("show people: ./app 'people'")

    def print_logout_commands(self):
        print("Welcome to the App!\n")
        print("login: ./app 'login <username> <password>'")
        print("join: ./app 'join'")
        print("create: ./app 'create username=\"<value>\" password=\"<value>\" name=\"<value>\" status=\"<value>\"'")
        print("people: ./app 'people'")

    def print_session_home(self, username, session_token):
        person = self.app.get_person(username)
        print(f"Welcome back to the App, {person.name}!\n")
        print(f'"{person.status}"\n')
        print(f"edit: ./app 'session {session_token} edit'")
        print(f"update: ./app 'session {session_token} update (name=\"<value>\"|status=\"<value>\")+'")
        print(f"logout: ./app 'session {session_token} logout'")
        print(f"people: ./app '[session {session_token} ]people'")

if __name__ == "__main__":
    session_file_path = 'sessions.json'
    app = RESTfulTerminalApp(session_file=session_file_path)
    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        app.run(command)
    else:
        app.run()
