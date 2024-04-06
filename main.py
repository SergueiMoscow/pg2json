import os
import re
import tkinter as tk
from tkinter import ttk, Text
from typing import List, Tuple

from services import utils
from services.pg2json import table_to_json
from services.utils import get_connection, get_applications, get_app_config, get_databases, get_db_config, \
    get_backup_full_dir


def get_tables_by_app_and_db_config(app_name, db_config_name) -> List[str]:
    db_settings = get_db_config(app_name, db_config_name)
    dsn = db_settings['dsn']
    schema = db_settings['schema']
    table_names = utils.get_tables(dsn, schema)
    return table_names


def get_app_backup_dir(app_name) -> str:
    app_settings = get_app_config(app_name)
    return str(os.path.join(app_settings['backup_dir'], app_name))


def get_existing_backups(app_name) -> List[str]:
    backup_dir = get_app_backup_dir(app_name)
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    backups = []
    if os.path.exists(backup_dir) and os.path.isdir(backup_dir):
        for server_name in os.listdir(backup_dir):
            backup_dir_with_server = os.path.join(backup_dir, server_name)
            for root, dirs, files in os.walk(backup_dir_with_server):
                for dir_name in dirs:
                    if re.match(date_pattern, dir_name):
                        backups.append(f'{server_name} / {dir_name}')

    return backups


def get_json_files(path: str) -> List[str]:
    json_files = []
    for file in os.listdir(path):
        if file.endswith(".json"):
            json_files.append(os.path.splitext(file)[0])
    return json_files


def get_default_app_tables(app) -> List[str]:
    app = get_app_config(app)
    tables = app.get('tables')
    if tables is None:
        return []
    return tables


def get_backup_files(app_name: str, dir_date_backup: str) -> List[str]:
    backup_dir = get_app_backup_dir(app_name)
    return get_json_files(os.path.join(backup_dir, dir_date_backup))


def save_db_config(application, database):
    print(f"Saving configuration for {application} and {database}")


def backup(application, database, tables):
    print(f"Backup started for {application} and {database}")
    backup_full_dir = get_backup_full_dir(application, database)
    config = get_db_config(application, database)
    with get_connection(config['dsn']) as conn:
        for table in tables:
            output_file = os.path.join(backup_full_dir, f'{table}.json')
            table_to_json(conn=conn, schema=config['schema'], table=table, output_file=output_file)


def restore(application, database):
    print(f"Restore started for {application} and {database}")


class Application:
    def __init__(self, root):
        self.root = root
        self.cur_app_selection = tk.StringVar(self.root)
        self.cur_db_selection = tk.StringVar(self.root)
        self.root.geometry("900x550")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.app_listbox = None
        self.db_listbox = None
        self.tables_listbox = None
        self.backups_combobox = None  # Даты / папки
        self.backups_listbox = None   # Таблицы / json файлы
        self.db_params = None
        self.current_app = None
        self.current_db = None
        self.create_widgets()

    def create_widgets(self):

        # Applications
        frame_app = ttk.LabelFrame(self.root, text="Applications")
        frame_app.grid(row=0, column=0, rowspan=1, padx=10, pady=10, sticky="nesw")
        self.app_listbox = tk.Listbox(frame_app, width=30, listvariable=self.cur_app_selection)
        self.app_listbox.bind('<<ListboxSelect>>', self._app_click_handler)
        for item in get_applications():
            self.app_listbox.insert(tk.END, item)
        self.app_listbox.pack(expand=True, fill='both')

        # Databases
        frame_db = ttk.LabelFrame(self.root, text="Databases")
        frame_db.grid(row=0, column=1, rowspan=1, padx=10, pady=10, sticky="nesw")
        self.db_listbox = tk.Listbox(frame_db, width=30, listvariable=self.cur_db_selection)
        self.db_listbox.bind('<<ListboxSelect>>', self._db_list_click_handler)
        self.db_listbox.pack(expand=True, fill='both')

        # Tables
        frame_tables = ttk.LabelFrame(self.root, text="Таблицы")
        frame_tables.grid(row=0, column=2, rowspan=1, padx=10, pady=10, sticky="nesw")
        self.tables_listbox = tk.Listbox(frame_tables, width=30, selectmode=tk.MULTIPLE)
        self.tables_listbox.pack(expand=True, fill='both')

        # Backups
        frame_backups = ttk.LabelFrame(self.root, text="Бэкапы")
        frame_backups.grid(row=0, column=3, padx=10, pady=10, sticky="nesw")
        self.backups_combobox = ttk.Combobox(frame_backups, state='readonly', width=30)
        self.backups_combobox.bind('<<ComboboxSelected>>', self._backup_dirs_select_handler)
        self.backups_combobox.pack(expand=False, fill='both')

        self.backups_listbox = tk.Listbox(frame_backups, width=30, selectmode=tk.MULTIPLE)
        self.backups_listbox.pack(expand=False, fill='both')

        # Config
        frame_params = ttk.LabelFrame(self.root, text="Database Parameters")
        frame_params.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nesw")
        self.db_params = Text(frame_params, height=7)
        self.db_params.pack(expand=True, fill='both')

        # Buttons config
        save_button = ttk.Button(frame_params, text="Save", command=self.save_config)
        save_button.pack(side=tk.LEFT, padx=5)
        cancel_button = ttk.Button(frame_params, text="Cancel", command=self._load_db_config)
        cancel_button.pack(side=tk.LEFT, padx=5)

        # Action buttons
        frame_ops = ttk.Frame(self.root)
        frame_ops.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nesw")

        backup_button = ttk.Button(frame_ops, text="Backup", command=self._backup)
        backup_button.pack(side=tk.LEFT, padx=5)

        restore_button = ttk.Button(frame_ops, text="Restore", command=restore)
        restore_button.pack(side=tk.LEFT, padx=5)

        close_button = ttk.Button(frame_ops, text="Close", command=self.root.destroy)
        close_button.pack(side=tk.LEFT, padx=5)

    def _app_click_handler(self, evt):
        self.current_db = None
        self.db_params.delete(1.0, tk.END)
        cur_app_selection = self.app_listbox.curselection()
        if cur_app_selection:
            app = self.app_listbox.get(self.app_listbox.curselection())
            databases = get_databases(app)
            self.db_listbox.delete(0, tk.END)
            for item in databases:
                self.db_listbox.insert(tk.END, item)

    def _db_list_click_handler(self, evt):
        # Подгружаем конфиг
        db_index = self.db_listbox.curselection()
        if len(db_index) > 0:
            self.current_db = self.db_listbox.get(db_index)
        self._load_db_config(evt)
        # Подгружаем таблицы
        app, db = self._get_selected_app_and_db()
        self.tables_listbox.delete(0, tk.END)
        if app and db:
            tables = get_tables_by_app_and_db_config(app, db)
            for table in tables:
                self.tables_listbox.insert(tk.END, table)
        # Подгружаем имеющиеся бэкапы
        self._load_backup_dirs()
        self._select_default_backup_tables()

    def _get_selected_app_and_db(self) -> Tuple[str, str]:
        app = self.app_listbox.get('active')
        db = self.current_db
        # db_index = self.db_listbox.curselection()
        # if db_index:
        #     db = self.db_listbox.get(db_index)  # get('active')
        #     print('app, db: ', app, db)
        return app, db

    def _load_db_config(self, evt):
        app, db = self._get_selected_app_and_db()
        self.db_params.delete(1.0, tk.END)
        text = ''
        if app and db:
            db_config = get_db_config(app, db)
            for k, v in db_config.items():
                text += k + ' = ' + v + '\n'

            self.db_params.insert(tk.END, text)

    def _load_backup_dirs(self):
        app, db = self._get_selected_app_and_db()
        dirs = get_existing_backups(app)
        self.backups_combobox['values'] = dirs

    def _backup_dirs_select_handler(self, evt):
        app, db = self._get_selected_app_and_db()
        backup_db, backup_date = [part.strip() for part in self.backups_combobox.get().split('/')]
        dir_backup = str(os.path.join(backup_db, backup_date))

        json_files = get_backup_files(app, dir_backup)
        self.backups_listbox.delete(0, tk.END)
        for json_file in json_files:
            self.backups_listbox.insert(tk.END, json_file)

    def _select_default_backup_tables(self):
        app, db = self._get_selected_app_and_db()
        tables = get_default_app_tables(app)
        if len(tables) == 0:
            # select all tables
            for i in range(self.tables_listbox.size()):
                self.tables_listbox.selection_set(i)
        else:
            # select configured tables
            for i in range(self.tables_listbox.size()):
                if self.tables_listbox.get(i) in tables:
                    self.tables_listbox.selection_set(i)

    def _backup(self):
        app, db = self._get_selected_app_and_db()
        selected_indices = self.tables_listbox.curselection()
        selected_tables = [self.tables_listbox.get(idx) for idx in selected_indices]
        backup(app, db, selected_tables)

    def save_config(self):
        application = self.app_listbox.get()
        database = self.db_listbox.get()
        save_db_config(application, database)


def run():
    root = tk.Tk()
    root.title('PostgreSQL - JSON backup utility')
    app = Application(root)
    root.mainloop()


run()
