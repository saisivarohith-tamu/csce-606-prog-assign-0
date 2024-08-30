#!/bin/bash

# Usage: ./app <command>
# Example: ./app create username="pcr" password="qwertyuiop" name="prof. ritchey" status="demonstrating"

# Check if command is passed
if [ "$#" -eq 0 ]; then
    # Default to 'home' if no command is provided
    command="home"
else
    # Combine all arguments into a single command string
    command="$*"
fi

# Call the Python script with the command
python3 src/main.py "$command"
