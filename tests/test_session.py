#!/usr/bin/python3

# test/test_session.py
import pytest
from session import Session

# Test to initialize a Session object
def test_session_initialization():
    session = Session("test_token", "test_user")
    assert session.token == "test_token"
    assert session.username == "test_user"

# Test converting a Session object to a dictionary
def test_session_to_dict():
    session = Session("test_token", "test_user")
    session_dict = session.to_dict()
    assert session_dict == {
        "token": "test_token",
        "username": "test_user"
    }

# Test converting a dictionary to a Person object
def test_session_from_dict():
    session_data = {
        "token": "test_token",
        "username": "test_user"
    }
    session = Session.from_dict(session_data)
    assert session.token == "test_token"
    assert session.username == "test_user"
