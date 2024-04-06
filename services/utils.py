import contextlib
import datetime
import json
import os
import psycopg2

SETTINGS_JSON = 'config.json'


@contextlib.contextmanager
def get_connection(dsn: str):
    conn = None
    try:
        conn = psycopg2.connect(dsn)
        yield conn
    except psycopg2.DatabaseError as e:
        print("Ошибка при работе с PostgreSQL", e)
        raise psycopg2.DatabaseError from e
    finally:
        if conn is not None:
            conn.close()


def get_tables(dsn: str, schema: str):
    with get_connection(dsn) as conn:
        cursor = conn.cursor()
        query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}';"
        cursor.execute(query)
        table_names_list = []
        for row in cursor:
            table_names_list.append(row[0])
        return table_names_list


def get_settings():
    with open(SETTINGS_JSON) as f:
        settings = json.load(f)
    return settings


def get_applications():
    settings = get_settings()
    applications = [app['application'] for app in settings]
    print(applications)
    return applications


def get_app_config(app: str) -> dict:
    settings = get_settings()
    database_names = []
    for app_config in settings:
        if app_config['application'] == app:
            return app_config
    return {}


def get_databases(app):
    settings = get_settings()
    database_names = []
    for app_config in settings:
        if app_config['application'] == app:
            for db in app_config['databases']:
                database_names.append(db["name"])
    print(database_names)
    return database_names


def get_db_config(app_name, db_config_name):
    settings = get_settings()
    db_config = {}
    for app in settings:
        if app['application'] == app_name:
            for db in app['databases']:
                if db['name'] == db_config_name:
                    db_config = db['config']
    return db_config


def get_backup_full_dir(app_name, db_config_name) -> str:
    app_config = get_app_config(app_name)
    date_y_m_d = datetime.datetime.now().strftime('%Y-%m-%d')
    dir_full_path = os.path.join(app_config['backup_dir'], app_name, db_config_name, date_y_m_d)

    if not os.path.exists(dir_full_path):
        try:
            os.makedirs(dir_full_path)
        except OSError as e:
            print(f'Ошибка при создании каталога {dir_full_path}')
            raise OSError from e
    else:
        print(f'Каталог {dir_full_path} уже существует')
        raise OSError('Каталог уже существует')

    return str(dir_full_path)
