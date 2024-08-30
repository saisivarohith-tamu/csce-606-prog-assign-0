#!/usr/bin/python3

# src/app.py
import json
from person import Person
from datetime import datetime
import re

class Application:
    def __init__(self, data_file='data.json'):
        self.data_file = data_file
        self.people = self.load_people()

    def load_people(self):
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                return {username: Person(**info) for username, info in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_people(self):
        with open(self.data_file, 'w') as file:
            json.dump({username: person.to_dict() for username, person in self.people.items()}, file, default=str)

    def create_person(self, username=None, password=None, name=None, status=None):
        if username is None:
            return "failed to create: missing username"
        
        normalized_username = username.lower()

        if len(normalized_username) < 3:
            return "failed to create: username is too short"
        if len(normalized_username) > 20:
            return "failed to create: username is too long"
        if not re.match(r'^\w+$', normalized_username):  # Check for alphanumeric and underscores
            return "failed to create: invalid username"
        if password is None:
            return "failed to create: missing password"
        if name is None:
            return "failed to create: missing name"
        if status is None:
            return "failed to create: missing status"

        if len(name) < 1:
            return "failed to create: name is too short"
        if len(name) > 30:
            return "failed to create: name is too long"

        # Check if the user already exists (case-insensitive check)
        if normalized_username in (user.lower() for user in self.people):
            return f"failed to create: {username} is already registered"

        # Check for double quotes in input
        if '"' in username:
            return 'failed to create: username contains double quote'
        if '"' in password:
            return 'failed to create: password contains double quote'
        if '"' in name:
            return 'failed to create: name contains double quote'
        if '"' in status:
            return 'failed to create: status contains double quote'

        # New validation logic for status
        if not status or len(status) > 100:
            reason = "short" if not status else "long"
            return f"failed to create: status is too {reason}"

        if not self._is_valid_password(password):
            return "failed to create: password is too short"

        # Create the new person
        person = Person(normalized_username, password, name, status)
        self.people[username] = person
        self.save_people()
        return "success"

    def update_person(self, username, name=None, status=None):
        if username not in self.people:
            return f"failed to update: user '{username}' not found"
        
        person = self.people[username]
        update_data = {}

        # Correctly update the name if provided
        if name is not None and name != person.name:
            if len(name) < 1:
                return "failed to update: name is too short"
            if len(name) > 30:
                return "failed to update: name is too long"
            update_data['name'] = name

        # Correctly update the status if provided
        if status is not None and status != person.status:
            if len(status) > 100:
                return "failed to update: status is too long"
            if len(status) == 0:
                return "failed to update: status is too short"
            update_data['status'] = status

        # Apply updates only if there are changes
        if update_data:
            person.update(**update_data)
            self.save_people()
            return "success"
        else:
            return ""  # No changes made

    def _is_valid_password(self, password):
        # password should not be empty and must be at least 4 characters
        if not password or len(password) < 4:
            return False
        return True

    def get_person(self, username):
        return self.people.get(username)

    def authenticate_user(self, username, password):
        person = self.get_person(username)
        if isinstance(person, Person) and person.password == password:
            return person.to_dict()
        return "access denied: incorrect username or password\nhome: ./app"

    def list_people(self):
        people_list = [
            {
                "username": person.username,
                "name": person.name,
                "status": person.status,
                "updated_at": person.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for person in self.people.values()
        ]
        return sorted(people_list, key=lambda x: x["updated_at"], reverse=True)

    def find_people(self, pattern, return_message=False):
        search_field = None
        search_value = None

        # Check if the pattern is empty and set search_value to empty string
        if not pattern.strip():
            search_field = None
            search_value = ""
        elif ':' in pattern:
            search_field, search_value = pattern.split(':', 1)
            search_field = search_field.strip().lower()
            search_value = search_value.strip().lower()
        else:
            search_value = pattern.strip().lower()

        def match_person(person, field, value):
            if field == 'username':
                return value in person.username.lower()
            elif field == 'name':
                return value in person.name.lower()
            elif field == 'status':
                return value in person.status.lower()
            elif field == 'updated':
                return value in person.updated_at.strftime("%Y-%m-%d %H:%M:%S").lower()
            else:
                # Perform a general match across all fields if no specific field is given
                return (value in person.username.lower() or
                        value in person.name.lower() or
                        value in person.status.lower() or
                        value in person.updated_at.strftime("%Y-%m-%d %H:%M:%S").lower())

        results = [
            person for person in self.people.values()
            if match_person(person, search_field, search_value)
        ]

        if return_message:
            if not search_field and not search_value:
                message = "People (find all)"
            elif not search_field:
                field_name = 'any'
                message = f'People (find "{search_value}" in {field_name})'
            elif search_field == 'updated':
                field_name = 'updated at'
                message = f'People (find "{search_value}" in {field_name})'
            else:
                message = f'People (find "{search_value}" in {search_field})'
            return results, message

        return results

    def sort_people(self, key, order='asc'):
        valid_keys = ['name', 'username', 'status', 'updated']
        if key not in valid_keys:
            print(f"Invalid key: {key}. Valid keys are {', '.join(valid_keys)}.")
            return []

        reverse_order = order == 'desc'
        if key == 'updated':
            return sorted(self.list_people(), key=lambda x: x['updated_at'], reverse=reverse_order)
        return sorted(self.list_people(), key=lambda x: x[key], reverse=reverse_order)

    def edit_person(self, username):
        person = self.get_person(username)
        if not person:
            print(f"Person with username '{username}' not found.")
            return

        new_status = input("Enter new status: ").strip()
        if new_status:
            person.status = new_status
            person.updated_at = datetime.now()
            print(f"{person.name}'s status has been updated to: \"{person.status}\"")
        else:
            print("No changes made.")

    def delete_person(self, username):
        if username not in self.people:
            return f"failed to delete: user '{username}' not found"
        del self.people[username]
        self.save_people()
        return "success"
