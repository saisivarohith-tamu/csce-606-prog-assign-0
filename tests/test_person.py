#!/usr/bin/python3

# test/test_person.py
import pytest
from datetime import datetime
from person import Person

# Create a Person object with an explicit updated_at date
def test_person_initialization_with_updated_at():
    updated_at = "2024-08-24 12:00:00"
    person = Person("test_user", "password123", "Test User", "Active", updated_at)
    
    assert person.username == "test_user"
    assert person.password == "password123"
    assert person.name == "Test User"
    assert person.status == "Active"
    assert person.updated_at == datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")

# Create a Person object without specifying updated_at
def test_person_initialization_without_updated_at():
    person = Person("test_user", "password123", "Test User", "Active")
    
    assert person.username == "test_user"
    assert person.password == "password123"
    assert person.name == "Test User"
    assert person.status == "Active"
    assert person.updated_at is not None  # updated_at should be set to the current time

# Test updating attributes using the update method
def test_person_update():
    person = Person("test_user", "password123", "Test User", "Active")
    
    # Capture current updated_at time
    old_updated_at = person.updated_at
    
    # Perform update
    person.update(name="Updated User", status="Inactive")
    
    assert person.name == "Updated User"
    assert person.status == "Inactive"
    assert person.updated_at > old_updated_at  # updated_at should be refreshed

# Test updating a non-existent attribute (should not throw error)
def test_person_update_non_existent_attribute():
    person = Person("test_user", "password123", "Test User", "Active")
    
    # Perform update with a non-existent attribute
    person.update(non_existent="This should not do anything")
    
    # Assert that nothing has changed
    assert not hasattr(person, 'non_existent')  # Person should not have this attribute

 # Test converting a Person object to a dictionary
def test_person_to_dict():
    updated_at = "2024-08-24 12:00:00"
    person = Person("test_user", "password123", "Test User", "Active", updated_at)
    person_dict = person.to_dict()
    
    assert person_dict == {
        "username": "test_user",
        "password": "password123",
        "name": "Test User",
        "status": "Active",
        "updated_at": updated_at
    }
