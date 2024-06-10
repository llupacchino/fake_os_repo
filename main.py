import requests
import zipfile
import io
import random
import time
import os
import shutil
import json
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from cryptography.fernet import Fernet, InvalidToken
import importlib


class FakeShell:
    def __init__(self, save_file='fake_os_filesystem.json'):
        self.commands = {
            'help': self.help,
            'exit': self.exit,
            'ls': self.ls,
            'touch': self.touch,
            'rm': self.rm,
            'mkdir': self.mkdir,
            'rmdir': self.rmdir,
            'ps': self.ps,
            'edit': self.edit,
            'cat': self.cat,
            'save': self.save,
            'convo': self.convo,
            'dl': self.dl
        }
        self.running = True
        self.file_system = FakeFileSystem(save_file)
        self.process_manager = FakeProcessManager()
        self.package_repo_url = "https://raw.githubusercontent.com/llupacchino/fake_os_repo/main/packages.json"
        self.local_packages_file = "local_packages.json"
        self.packages_dir = "packages"
        self.available_packages = []

        if not os.path.exists(self.packages_dir):
            os.makedirs(self.packages_dir)

    def run(self):
        self.matrix_boot_effect()
        self.file_system.load_state()
        self.load_local_packages()
        self.load_installed_packages()
        while self.running:
            command = input("fakeOS> ")
            self.execute_command(command.split())
        self.file_system.save_state()

    def execute_command(self, args):
        if args:
            command = args[0]
            if command in self.commands:
                self.commands[command](args[1:])
            else:
                print(f"Command not found: {command}")

    def help(self, args):
        print("Available commands: " + ", ".join(self.commands.keys()))

    def exit(self, args):
        print("Exiting fakeOS...")
        self.running = False

    def ls(self, args):
        self.file_system.list_files()

    def touch(self, args):
        if args:
            self.file_system.create_file(args[0])
        else:
            print("touch: missing file name")

    def rm(self, args):
        if args:
            self.file_system.delete_file(args[0])
        else:
            print("rm: missing file name")

    def mkdir(self, args):
        if args:
            self.file_system.create_directory(args[0])
        else:
            print("mkdir: missing directory name")

    def rmdir(self, args):
        if args:
            self.file_system.delete_directory(args[0])
        else:
            print("rmdir: missing directory name")

    def ps(self, args):
        self.process_manager.list_processes()

    def edit(self, args):
        if args:
            self.file_system.edit_file(args[0])
        else:
            print("edit: missing file name")

    def cat(self, args):
        if args:
            self.file_system.view_file(args[0])
        else:
            print("cat: missing file name")

    def save(self, args):
        self.file_system.save_state()
        print("Filesystem state saved.")

    def convo(self, args):
        if len(args) == 1 and args[0] == '-S':
            username = input("Enter your username: ")
            server = ChatServer(username)
            server.start_server()
        elif len(args) == 2 and args[0] == '-C':
            username = input("Enter your username: ")
            client = ChatClient(args[1], username)
            client.start_client()
        else:
            print("Invalid usage. Use 'convo -S' to start a server or 'convo -C <IP>' to connect to a server.")

    def dl(self, args):
        if len(args) == 1:
            if args[0] == '-list':
                self.list_packages()
            elif args[0] == '-update':
                self.update_package_list()
            else:
                self.download_package(args[0][1:])
        else:
            print(
                "Invalid usage. Use 'dl -list' to list packages, 'dl -update' to update package list, or 'dl -{package_name}' to download a package.")

    def list_packages(self):
        print("Available packages:")
        for package in self.available_packages:
            print(f"- {package['name']} ({package['version']}): {package['description']}")

    def update_package_list(self):
        try:
            response = requests.get(self.package_repo_url)
            response.raise_for_status()
            self.available_packages = response.json().get('packages', [])
            with open(self.local_packages_file, 'w') as f:
                json.dump(self.available_packages, f)
            print("Package list updated.")
        except requests.RequestException as e:
            print(f"Failed to update package list: {e}")

    def download_package(self, package_name):
        package = next((pkg for pkg in self.available_packages if pkg['name'] == package_name), None)
        if not package:
            print(f"Package '{package_name}' not found.")
            return

        try:
            response = requests.get(package['url'])
            response.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(self.packages_dir)
            print(f"Package '{package_name}' downloaded and extracted.")
            self.load_installed_package(package)
        except requests.RequestException as e:
            print(f"Failed to download package '{package_name}': {e}")

    def load_local_packages(self):
        if os.path.exists(self.local_packages_file):
            with open(self.local_packages_file, 'r') as f:
                self.available_packages = json.load(f)

    def load_installed_packages(self):
        for package in self.available_packages:
            if 'file' in package:
                package_file = os.path.join(self.packages_dir, package['file'])
                if os.path.exists(package_file):
                    self.load_installed_package(package)
            else:
                print(f"Package '{package['name']}' is missing the 'file' key.")

    def load_installed_package(self, package):
        package_file = os.path.join(self.packages_dir, package['file'])
        spec = importlib.util.spec_from_file_location(package['name'], package_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'register'):
            module.register(self)
        print(f"Package '{package['name']}' loaded.")

    def matrix_boot_effect(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()-_=+[{]}|;:'\",<.>/?`~"

        # Attempt to get terminal size, use default if it fails
        try:
            width, height = shutil.get_terminal_size()
        except OSError:
            width, height = 80, 24  # Default terminal size

        for _ in range(height):
            line = ''.join(random.choice(chars) for _ in range(width))
            print(line)
            time.sleep(0.05)

        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')

        # ASCII Art
        ascii_art = """
FFFFFFFFFFFFFFFFFFFFFF                kkkkkkkk                                                         OOOOOOOOO        SSSSSSSSSSSSSSS 
F::::::::::::::::::::F                k::::::k                                                       OO:::::::::OO    SS:::::::::::::::S
F::::::::::::::::::::F                k::::::k                                                     OO:::::::::::::OO S:::::SSSSSS::::::S
FF::::::FFFFFFFFF::::F                k::::::k                                                    O:::::::OOO:::::::OS:::::S     SSSSSSS
  F:::::F       FFFFFFaaaaaaaaaaaaa    k:::::k    kkkkkkk eeeeeeeeeeee                            O::::::O   O::::::OS:::::S            
  F:::::F             a::::::::::::a   k:::::k   k:::::kee::::::::::::ee                          O:::::O     O:::::OS:::::S            
  F::::::FFFFFFFFFF   aaaaaaaaa:::::a  k:::::k  k:::::ke::::::eeeee:::::ee                        O:::::O     O:::::O S::::SSSS         
  F:::::::::::::::F            a::::a  k:::::k k:::::ke::::::e     e:::::e                        O:::::O     O:::::O  SS::::::SSSSS    
  F:::::::::::::::F     aaaaaaa:::::a  k::::::k:::::k e:::::::eeeee::::::e                        O:::::O     O:::::O    SSS::::::::SS  
  F::::::FFFFFFFFFF   aa::::::::::::a  k:::::::::::k  e:::::::::::::::::e                         O:::::O     O:::::O       SSSSSS::::S 
  F:::::F            a::::aaaa::::::a  k:::::::::::k  e::::::eeeeeeeeeee                          O:::::O     O:::::O            S:::::S
  F:::::F           a::::a    a:::::a  k::::::k:::::k e:::::::e                                   O::::::O   O::::::O            S:::::S
FF:::::::FF         a::::a    a:::::a k::::::k k:::::ke::::::::e                                  O:::::::OOO:::::::OSSSSSSS     S:::::S
F::::::::FF         a:::::aaaa::::::a k::::::k  k:::::ke::::::::eeeeeeee                           OO:::::::::::::OO S::::::SSSSSS:::::S
F::::::::FF          a::::::::::aa:::ak::::::k   k:::::kee:::::::::::::e                             OO:::::::::OO   S:::::::::::::::SS 
FFFFFFFFFFF           aaaaaaaaaa  aaaakkkkkkkk    kkkkkkk eeeeeeeeeeeeee                               OOOOOOOOO      SSSSSSSSSSSSSSS   
                                                                          ________________________                                      
                                                                          _::::::::::::::::::::::_                                      
                                                                          ________________________                                      
"""
        print(ascii_art)
        time.sleep(2)  # Pause for a moment to display the ASCII art


class FakeFileSystem:
    def __init__(self, save_file):
        self.files = {}
        self.directories = set()
        self.save_file = save_file
        self.key_file = 'secret.key'
        self.key = self.load_key()

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as key_file:
            key_file.write(key)
        return key

    def load_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as key_file:
                return key_file.read()
        else:
            return self.generate_key()

    def encrypt_data(self, data):
        fernet = Fernet(self.key)
        return fernet.encrypt(data.encode())

    def decrypt_data(self, data):
        fernet = Fernet(self.key)
        try:
            return fernet.decrypt(data).decode()
        except InvalidToken as e:
            print("Invalid Token: Decryption failed")
            return None

    def list_files(self):
        print("Files:", ", ".join(self.files.keys()))
        print("Directories:", ", ".join(self.directories))

    def create_file(self, filename):
        if filename.endswith('.txt'):
            self.files[filename] = ""
            print(f"Text file created: {filename}")
        else:
            print("Only .txt files can be created with touch command.")

    def delete_file(self, filename):
        if filename in self.files:
            del self.files[filename]
            print(f"File deleted: {filename}")
        else:
            print(f"File not found: {filename}")

    def create_directory(self, dirname):
        self.directories.add(dirname)
        print(f"Directory created: {dirname}")

    def delete_directory(self, dirname):
        if dirname in self.directories:
            self.directories.remove(dirname)
            print(f"Directory deleted: {dirname}")
        else:
            print(f"Directory not found: {dirname}")

    def edit_file(self, filename):
        if filename in self.files:
            print("Opening text editor (type 'exit' to save and quit)...")
            while True:
                line = input()
                if line == 'exit':
                    break
                self.files[filename] += line + "\n"
            print(f"File saved: {filename}")
        else:
            print(f"File not found: {filename}")

    def view_file(self, filename):
        if filename in self.files:
            print(f"Content of {filename}:\n{self.files[filename]}")
        else:
            print(f"File not found: {filename}")

    def save_state(self):
        state = {
            'files': self.files,
            'directories': list(self.directories)
        }
        encrypted_data = self.encrypt_data(json.dumps(state))
        with open(self.save_file, 'wb') as f:
            f.write(encrypted_data)
        print("Filesystem state saved.")

    def load_state(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = self.decrypt_data(encrypted_data)
                if decrypted_data:
                    state = json.loads(decrypted_data)
                    self.files = state.get('files', {})
                    self.directories = set(state.get('directories', []))
                    print("Filesystem state loaded.")
                else:
                    print("Failed to load filesystem state: Decryption failed")
        else:
            print("No saved filesystem state found.")


class FakeProcessManager:
    def __init__(self):
        self.processes = ["init"]

    def list_processes(self):
        print("Running processes:", ", ".join(self.processes))


class ChatServer:
    def __init__(self, username, host='0.0.0.0', port=12345):
        self.username = username
        self.host = host
        self.port = port
        self.clients = []
        self.running = True
        self.gui = ChatGUI(self)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Chat server started on {self.host}:{self.port}")

        accept_thread = threading.Thread(target=self.accept_clients)
        accept_thread.start()

        self.gui.run()

        self.running = False
        accept_thread.join()
        self.server_socket.close()
        for client in self.clients:
            client.close()

    def accept_clients(self):
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append(client_socket)
                print(f"Client connected from {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except socket.error:
                break

    def handle_client(self, client_socket):
        while self.running:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    self.gui.display_message(message)
                    self.broadcast(message, client_socket)
                else:
                    client_socket.close()
                    break
            except socket.error:
                break

    def broadcast(self, message, client_socket):
        for client in self.clients:
            if client != client_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    client.close()
                    self.clients.remove(client)

    def send_message(self, message):
        message = f"{self.username}: {message}"
        self.gui.display_message(message)
        self.broadcast(message, None)

    def stop(self):
        self.running = False
        self.server_socket.close()


class ChatClient:
    def __init__(self, host, username, port=12345):
        self.host = host
        self.port = port
        self.username = username
        self.running = True
        self.gui = ChatGUI(self)

    def start_client(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to chat server at {self.host}:{self.port}")

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        self.gui.run()

        self.running = False
        receive_thread.join()
        self.client_socket.close()

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.gui.display_message(message)
            except socket.error:
                break

    def send_message(self, message):
        message = f"{self.username}: {message}"
        self.gui.display_message(message)
        self.client_socket.send(message.encode('utf-8'))

    def stop(self):
        self.running = False
        self.client_socket.close()


class ChatGUI:
    def __init__(self, chat_instance):
        self.chat_instance = chat_instance
        self.root = tk.Tk()
        self.root.title("Chat")

        self.chat_window = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.chat_window.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.chat_window.config(state=tk.DISABLED)

        self.entry_field = tk.Entry(self.root)
        self.entry_field.pack(padx=20, pady=10, fill=tk.X, expand=True)
        self.entry_field.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def display_message(self, message):
        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.insert(tk.END, message + "\n")
        self.chat_window.config(state=tk.DISABLED)
        self.chat_window.yview(tk.END)

    def send_message(self, event=None):
        message = self.entry_field.get()
        self.entry_field.delete(0, tk.END)
        self.chat_instance.send_message(message)

    def on_closing(self):
        self.chat_instance.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    shell = FakeShell()
    shell.run()