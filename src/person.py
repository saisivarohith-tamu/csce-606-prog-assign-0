#!/usr/bin/python3

# src/person.py
from datetime import datetime

class Person:
    def __init__(self, username, password, name, status, updated_at=None):
        self.username = username
        self.password = password
        self.name = name
        self.status = status
        if isinstance(updated_at, datetime):
            self.updated_at = updated_at
        else:
            self.updated_at = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S") if updated_at else datetime.now()

    # Dynamic updates to the attributes of a Person instance using keyword arguments
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "name": self.name,
            "status": self.status,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
