#!/usr/bin/python3

# test/test_app.py
import unittest
from unittest.mock import patch, mock_open
from app import Application
from person import Person
from datetime import datetime
import json

# Mock data as a module-level variable so that it can be used in decorators
mock_data = {
    "user1": {
        "username": "user1",
        "password": "password1",
        "name": "prof. ritchey",
        "status": "active",
        "updated_at": "2024-08-24 12:00:00"
    }
}
mock_data_json = json.dumps(mock_data)

class TestApplication(unittest.TestCase):

    def setUp(self):
        self.mock_person = Person(username="user1", password="password1", name="prof. ritchey", status="active")
        self.mock_person.updated_at = datetime.strptime("2024-08-24 12:00:00", "%Y-%m-%d %H:%M:%S")

    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    def test_load_people_no_file(self, mock_file):
        app = Application(data_file="nonexistent.json")
        self.assertEqual(app.people, {})

    @patch("builtins.open", new_callable=mock_open, read_data="invalid_json")
    def test_load_people_invalid_json(self, mock_file):
        app = Application(data_file="invalid.json")
        self.assertEqual(app.people, {})

    @patch("builtins.open", new_callable=mock_open, read_data=mock_data_json)
    def test_load_people_valid_data(self, mock_file):
        app = Application(data_file="data.json")
        self.assertEqual(len(app.people), 1)
        self.assertEqual(app.people["user1"].username, "user1")

    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    def test_save_people(self, mock_file):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        app.save_people()
        
        # Check that open was called with "w" to write to the file
        mock_file.assert_any_call("data.json", "w")
        
        # Get the mock file handle
        handle = mock_file()
        
        # Collect all write calls and concatenate their arguments
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        
        # Construct the expected write data as a single JSON string
        expected_write_data = json.dumps({
            "user1": {
                "username": "user1",
                "password": "password1",
                "name": "prof. ritchey",
                "status": "active",
                "updated_at": "2024-08-24 12:00:00"
            }
        }, default=str)
        
        # Assert the written data matches the expected data
        assert written_data == expected_write_data

    @patch("app.Application._is_valid_password", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    def test_create_person_success(self, mock_file, mock_password):
        app = Application(data_file="data.json")
        result = app.create_person("user2", "password2", "Jane Doe", "active")
        self.assertEqual(result, "success")
        self.assertIn("user2", app.people)

    @patch("app.Application._is_valid_password", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data=mock_data_json)
    def test_create_person_existing_user(self, mock_file, mock_password):
        app = Application(data_file="data.json")
        result = app.create_person("user1", "password1", "prof. ritchey", "active")
        self.assertEqual(result, "failed to create: user1 is already registered")

    @patch("app.Application._is_valid_password", return_value=False)
    def test_create_person_invalid_password(self, mock_password):
        app = Application(data_file="data.json")
        result = app.create_person("user2", "wrongpass", "Jane Doe", "active")
        self.assertEqual(result, "failed to create: password is too short")

    def test_create_person_status_too_long(self):
        app = Application(data_file="data.json")
        long_status = "a" * 101
        result = app.create_person("user2", "password2", "Jane Doe", long_status)
        self.assertEqual(result, "failed to create: status is too long")

    def test_update_person_success(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.update_person("user1", name="John Smith", status="inactive")
        self.assertEqual(result, "success")
        self.assertEqual(app.people["user1"].name, "John Smith")

    def test_update_person_not_found(self):
        app = Application(data_file="data.json")
        result = app.update_person("user2")
        self.assertEqual(result, "failed to update: user 'user2' not found")

    def test_update_person_status_too_long(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        long_status = "a" * 101
        result = app.update_person("user1", status=long_status)
        self.assertEqual(result, "failed to update: status is too long")

    def test_get_person(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        person = app.get_person("user1")
        self.assertEqual(person.username, "user1")

    def test_authenticate_user_success(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.authenticate_user("user1", "password1")
        self.assertEqual(result["username"], "user1")

    def test_authenticate_user_failure(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.authenticate_user("user1", "wrongpass")
        self.assertEqual(result, "access denied: incorrect username or password\nhome: ./app")

    def test_list_people(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        people_list = app.list_people()
        self.assertEqual(len(people_list), 1)
        self.assertEqual(people_list[0]["username"], "user1")

    def test_find_people(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.find_people("user")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].username, "user1")

    def test_sort_people(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        sorted_people = app.sort_people("username")
        self.assertEqual(len(sorted_people), 1)
        self.assertEqual(sorted_people[0]["username"], "user1")

    def test_delete_person_success(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.delete_person("user1")
        self.assertEqual(result, "success")
        self.assertNotIn("user1", app.people)

    def test_delete_person_not_found(self):
        app = Application(data_file="data.json")
        result = app.delete_person("user2")
        self.assertEqual(result, "failed to delete: user 'user2' not found")

    def test_delete_person_not_found(self):
        app = Application(data_file="data.json")
        result = app.delete_person("non_existent_user")
        self.assertEqual(result, "failed to delete: user 'non_existent_user' not found")

    def create_mock_person(name, username, status, updated_at=None):
        if not updated_at:
            updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return Person(username=username, password="password", name=name, status=status, updated_at=updated_at)
        
    def test_find_people(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        results, message = app.find_people("user", return_message=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(message, 'People (find "user" in any)')

    def test_find_people_display_updated(self):
        app = Application(data_file="data.json")
        app.people = {
            "user1": Person(username="user1", password="password1", name="prof. ritchey", status="active", updated_at=datetime.strptime("2024-08-24 12:00:00", "%Y-%m-%d %H:%M:%S"))
        }
        results, message = app.find_people("updated:2024-08-24", return_message=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(message, 'People (find "2024-08-24" in updated at)')

    def test_find_people_empty_search(self):
        app = Application(data_file="data.json")
        app.people = {
            "user1": self.mock_person
        }
        results = app.find_people("")
        self.assertEqual(len(results), 1)

    def test_find_people_malformed_input(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        results = app.find_people("invalid:input")
        self.assertEqual(results, [])

    def test_sort_people_by_name_asc(self):
        app = Application(data_file="data.json")
        app.people = {
            "user1": Person(username="user1", password="password1", name="prof. ritchey", status="active"),
            "user2": Person(username="user2", password="password2", name="Jane Doe", status="inactive")
        }
        sorted_people = app.sort_people("name", "asc")
        self.assertEqual(sorted_people[0]["name"], "Jane Doe")
        self.assertEqual(sorted_people[1]["name"], "prof. ritchey")

    def test_sort_people_by_name_desc(self):
        app = Application(data_file="data.json")
        app.people = {
            "user1": Person(username="user1", password="password1", name="prof. ritchey", status="active"),
            "user2": Person(username="user2", password="password2", name="Jane Doe", status="inactive")
        }
        sorted_people = app.sort_people("name", "desc")
        self.assertEqual(sorted_people[0]["name"], "prof. ritchey")
        self.assertEqual(sorted_people[1]["name"], "Jane Doe")

    def test_is_valid_password(self):
        app = Application(data_file="data.json")
        self.assertTrue(app._is_valid_password("validpassword"))
        # Assuming you add logic for invalid passwords:
        self.assertFalse(app._is_valid_password(""))

    def test_update_person_no_changes(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.update_person("user1")
        self.assertEqual(result, "")

    def test_update_person_no_changes(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.update_person("user1")
        self.assertEqual(result, "")

    @patch("builtins.input", lambda *args: "New Status")
    def test_edit_person(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        app.edit_person("user1")
        self.assertEqual(app.people["user1"].status, "New Status")

    def test_is_valid_password(self):
        app = Application(data_file="data.json")
        self.assertTrue(app._is_valid_password("validpassword"))
        self.assertFalse(app._is_valid_password(""))  # Empty password
        self.assertFalse(app._is_valid_password("123"))  # Too short

    def test_create_person_existing_username(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.create_person("user1", "password1", "prof. ritchey", "active")
        self.assertEqual(result, "failed to create: user1 is already registered")

    def test_sort_people_invalid_key(self):
        app = Application(data_file="data.json")
        app.people = {
            "user1": self.mock_person
        }
        result = app.sort_people("invalid_key")
        self.assertEqual(result, [])  # returns an empty list on invalid key

    def test_find_people_empty_search(self):
        app = Application(data_file="data.json")
        app.people = {
            "user1": self.mock_person
        }
        result = app.find_people("")
        self.assertEqual(len(result), 1)  # returns all people if no pattern is provided

    def test_edit_person_not_found(self):
        app = Application(data_file="data.json")
        app.people = {}
        result = app.edit_person("non_existent_user")
        self.assertIsNone(result)  # no return value if the person is not found

    def test_update_person_no_fields_provided(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.update_person("user1")
        self.assertEqual(result, "")  # this is the response when no updates are made

    def test_find_people_malformed_input(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.find_people("invalid_input:pattern")
        self.assertEqual(result, [])  # it returns an empty list on malformed input

    def test_delete_person_invalid_username(self):
        app = Application(data_file="data.json")
        result = app.delete_person("non_existent_user")
        self.assertEqual(result, "failed to delete: user 'non_existent_user' not found")

    def test_update_person_no_fields_provided(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.update_person("user1")
        self.assertEqual(result, "")

    def test_sort_people_invalid_key(self):
        app = Application(data_file="data.json")
        app.people = {
            "user1": self.mock_person
        }
        result = app.sort_people("invalid_key")
        self.assertEqual(result, [])  # returns an empty list on invalid sort key

    def test_delete_person_not_found(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.delete_person("non_existent_user")
        self.assertEqual(result, "failed to delete: user 'non_existent_user' not found")

    def test_update_person_no_updates(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.update_person("user1")  # No name or status provided, should result in no updates
        self.assertEqual(result, "")

    def test_find_people_malformed_input(self):
        app = Application(data_file="data.json")
        app.people = {"user1": self.mock_person}
        result = app.find_people("invalid:input")  # input is malformed
        self.assertEqual(result, [])  # Expecting no matches, hence an empty list

    def test_delete_person_user_not_found(self):
        app = Application(data_file="data.json")
        result = app.delete_person("non_existent_user")  # User doesn't exist in the database
        self.assertEqual(result, "failed to delete: user 'non_existent_user' not found")
