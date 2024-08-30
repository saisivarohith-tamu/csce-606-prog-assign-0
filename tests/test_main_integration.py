#!/usr/bin/python3

# test/test_main_integration.py
import subprocess
import sys
import os

# Test to run the script with 'people' as argument
def test_main_with_arguments():
    result = subprocess.run(
        [sys.executable, 'src/main.py', 'people'],
        capture_output=True,
        text=True
    )
    # Check if the script executed and expected output is present
    assert "People" in result.stdout
    assert result.returncode == 0

# Test to run the script without any arguments
def test_main_without_arguments():
    result = subprocess.run(
        [sys.executable, 'src/main.py'],
        input='exit\n',  # Provide input to exit the loop
        capture_output=True,
        text=True
    )
    # Check if the script executed and expected output is present
    assert "Welcome to the App!" in result.stdout
    assert result.returncode == 0
