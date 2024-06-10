import os
import socket
import subprocess
import requests

def ping(args):
    if len(args) != 1:
        print("Usage: hackerman -p <hostname>")
        return

    hostname = args[0]
    response = os.system(f"ping -c 4 {hostname}" if os.name != 'nt' else f"ping {hostname}")

    if response == 0:
        print(f"{hostname} is up!")
    else:
        print(f"{hostname} is down!")

def tracert(args):
    if len(args) != 1:
        print("Usage: hackerman -t <hostname>")
        return

    hostname = args[0]
    command = f"tracert {hostname}" if os.name == 'nt' else f"traceroute {hostname}"
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(result.stdout)

def netstat(args):
    command = "netstat -an" if os.name == 'nt' else "netstat -a"
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(result.stdout)

def get_public_ip(args):
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        ip = response.json().get("ip")
        print(f"Public IP: {ip}")
    except requests.RequestException as e:
        print(f"Failed to get public IP: {e}")

def register(shell):
    shell.commands['hackerman'] = hackerman_command

def hackerman_command(args):
    if len(args) == 0:
        print("Usage: hackerman -p | -t | -n | -pip")
        return

    command = args[0]
    if command == '-p':
        ping(args[1:])
    elif command == '-t':
        tracert(args[1:])
    elif command == '-n':
        netstat(args[1:])
    elif command == '-pip':
        get_public_ip(args[1:])
    else:
        print(f"Unknown command: {command}")
