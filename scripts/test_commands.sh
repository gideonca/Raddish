#!/bin/bash

# Function to send command and print response
send_command() {
    echo "Sending: $1"
    echo "$1" | nc localhost 6379
    echo "---"
}

# Test basic commands
send_command "PING"
send_command "ECHO Hello Redis!"
send_command "SET testkey value123"
send_command "GET testkey"
send_command "EXPIRE testkey 5"
send_command "GET testkey"
sleep 6
send_command "GET testkey"  # Should return NULL after expiration
send_command "DEL testkey"
send_command "EXIT"