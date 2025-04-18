# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar
import psycopg2
import time
import threading
import os
import subprocess
from subprocess import Popen, PIPE
from datetime import datetime


def huh(table,name):
    backup = open(f"{name}.sql", "w+", encoding='utf-8')
    with open("backup_test.sql", encoding='utf-8') as file:
        lines = file.readlines()
        start = (lines.index(f"-- Name: {table}; Type: TABLE; Schema: public; Owner: postgres\n"))
        end = (lines.index(f"ALTER TABLE public.\"{table}\" OWNER TO postgres;\n"))
        for i in range(start-1,end+1):
            backup.write(lines[i])
        start = (lines.index(f"-- Data for Name: {table}; Type: TABLE DATA; Schema: public; Owner: postgres\n"))
        end = (lines.index(f"\.\n"))
        for i in range(start-1,end+1):
            backup.write(lines[i])
    backup.close()


class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup PostgreSQL")
        self.is_running = False
        self.backup_dir = "C:/backups"
        os.makedirs(self.backup_dir, exist_ok=True)

        # Настройки базы данных
        self.db_name = "postgres"
        self.user = "postgres"
        self.password = "%Пароль%"
        self.host = "%ip адрес%"
        self.port = "5432"

        # Кнопка для мгновенного создания резервной копии
        self.instant_backup_button = tk.Button(self.root, text="Мгновенная резервная копия", command=self.backup_database)
        self.instant_backup_button.pack(pady=10)

        # Кнопка для начала/остановки периодической задачи
        self.start_button = tk.Button(self.root, text="Запустить", command=self.start_backups)
        self.start_button.pack(pady=10)

        # Таймер
        self.timer_label = tk.Label(self.root, text="")
        self.timer_label.pack(pady=10)

    def start_backups(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(text="Остановить")
            threading.Thread(target=self.run_backup_task, daemon=True).start()
        else:
            self.is_running = False
            self.start_button.config(text="Запустить")

    def run_backup_task(self):
        while self.is_running:
            self.backup_database()
            time.sleep(300)  # 5 минут

    def backup_database(self):
        conn = psycopg2.connect(database=self.db_name, user=self.user, password=self.password, host=self.host, port=self.port)
        cursor = conn.cursor()


        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        cfg = (os.listdir("auto"))
        for i in cfg:
            print(i)
            backup_command = [
                "C:/Program Files/PostgreSQL/17/bin/pg_dump.exe",
                "-E", "UTF8",
                "-h", "%ip адрес%",  # Убедитесь, что IP-адрес корректен
                "-U", self.user,
                "-F", "c"  # Формат архива
            ]
            f = open(f"auto/{i}")
            lin = f.readlines()
            print(lin)
            if lin[0] == "full":
                backup_file = f"{self.backup_dir}/{i}_{timestamp}.sql"
                backup_command.append("-f")
                backup_command.append(backup_file)
            else:
                fil = open("fil.txt", "w+")
                a = ""
                for j in lin:
                    print(j)
                    text = j.replace("\n","")
                    unicode_representation = ''.join(f'\\u{ord(char):04x}' for char in text)
                    print(a)
                    fil.write(f"include table {unicode_representation}\n")
                fil.close()
                backup_command.append(f"--filter=fil.txt")
                backup_file = f"{self.backup_dir}/{i}_{timestamp}.sql"
                backup_command.append("-f")
                backup_command.append(backup_file)
            print(backup_command)
            backup_command.append(self.db_name)
            subprocess.call(backup_command, env=os.environ | {'PGPASSWORD': '1951'})
if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()
