import tkinter as tk
from tkinter import messagebox
import psycopg2
import pandas as pd
from datetime import datetime

# Настройки подключения к базе данных
DB_HOST = '%ip хоста%'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = '%пароль%'


# Функция для получения списка таблиц
def get_table_info():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE column_name = 'last_modified' AND table_schema='public'
    """)
    table_info = cursor.fetchall()
    cursor.close()
    conn.close()
    return table_info


# Функция для получения новых записей и имен столбцов
def fetch_new_records(table_name, last_modified):
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE last_modified > %s", (last_modified,))
    records = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]  # Получаем имена столбцов
    cursor.close()
    conn.close()
    return records, column_names


# Функция для записи в CSV
def write_to_csv(records, column_names, table_name):
    df = pd.DataFrame(records, columns=column_names)  # Создаем DataFrame с именами столбцов
    # Записываем в CSV с заголовками всегда
    df.to_csv(f'{table_name}_new_records.csv', mode='a', header=True, index=False)
    messagebox.showinfo("Success", f"New records from {table_name} have been written to {table_name}_new_records.csv")


# Основная функция
def check_for_new_records():
    table_info = get_table_info()
    for table, _ in table_info:
        try:
            new_records, column_names = fetch_new_records(table, last_modified_times[table])
            if new_records:
                write_to_csv(new_records, column_names, table)
                # Обновляем last_modified для последней записи
                last_modified_times[table] = max(
                    record[-1] for record in new_records)  # Предполагается, что last_modified - последний столбец
            else:
                messagebox.showinfo("Info", f"No new records found in {table}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

        # Обновляем last_modified для текущего времени
        last_modified_times[table] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(last_modified_times)


# Создание интерфейса
table_info1 = get_table_info()
last_modified_times = {table: '1970-01-01 00:00:00' for table, _ in table_info1}  # Начальное значение для last_modified

root = tk.Tk()
root.title("PostgreSQL to CSV")

check_button = tk.Button(root, text="Check for New Records", command=check_for_new_records)
check_button.pack(pady=20)

root.mainloop()
