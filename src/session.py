#!/usr/bin/python3

# src/session.py
class Session:
    def __init__(self, token, username):
        self.token = token
        self.username = username

    def to_dict(self):
        return {
            "token": self.token,
            "username": self.username
        }

    @classmethod
    def from_dict(cls, data):
        return cls(token=data['token'], username=data['username'])
