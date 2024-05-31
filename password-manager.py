import cmd
from cryptography.fernet import Fernet
import hashlib
import sqlite3
import os

class FileManagerCLI(cmd.Cmd):
    prompt = 'FileMngr>> '
    intro = 'Welcome to FileManagerCLI. Type "help" for available commands.'

    def __init__(self):
        super().__init__()
        if os.path.exists('master_password.txt'):
            self.master_password = input("Enter your master password: ")
            self.master_password_hash = hashlib.sha256(self.master_password.encode()).hexdigest()
            with open('master_password.txt', 'r') as f:
                stored_hash = f.read().strip()
                if self.master_password_hash == stored_hash:
                    print("You are now logged in!")
                else:
                    print("Incorrect password. Exiting.")
                    exit()
        else:
            self.master_password = input("Set a master password for the manager: ")
            self.master_password_hash = hashlib.sha256(self.master_password.encode()).hexdigest()
            with open('master_password.txt', 'w') as f:
                f.write(self.master_password_hash)
            print("Master password set successfully.")

        self.conn = self.connect_database()
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        print("I'm Ready")

    def connect_database(self):
        # connect to database
        conn = sqlite3.connect('password_manager.db')
        conn.execute(
        """
            CREATE TABLE IF NOT EXISTS manager(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """
        )
        return conn

    def do_save(self, data):
        args = data.split()
        if len(args) != 3:
            print("Usage: save <url> <username> <password>")
            return

        url, username, password = args
        encrypted_password = self.cipher_suite.encrypt(password.encode()).decode()

        conn = self.conn
        conn.execute(
        """
            INSERT INTO manager (url, username, password)
            VALUES (?, ?, ?)
        """, (url, username, encrypted_password)
        )
        conn.commit()
        print('Your password was successfully saved!')

    def do_delete(self, url):
        conn = self.conn
        conn.execute(
        """
            DELETE FROM manager WHERE url=?
        """, (url,)
        )
        conn.commit()
        print(f'Password for {url} deleted!')

    def do_list(self, line):
        conn = self.conn
        cursor = conn.execute(
        """
            SELECT url, username, password FROM manager
        """
        )
        for row in cursor:
            url, username, encrypted_password = row
            password = self.cipher_suite.decrypt(encrypted_password.encode()).decode()
            print(f'URL: {url}, Username: {username}, Password: {password}')

    def do_quit(self, line):
        self.conn.close()
        print("Goodbye!")
        return True

if __name__ == '__main__':
    FileManagerCLI().cmdloop()
