import datetime
import os
import urllib.parse

from services.pg2json import table_to_json
from services.utils import get_connection, get_tables


# if catalog exists return


# cycle per tables
if __name__ == '__main__':
    with get_connection() as conn:
        path = get_catalog()
        tables = get_tables(conn, schema)
        for table in tables:
            print(f'processing {table}')
            table_to_json(conn, schema, table, os.path.join(path, f'{table}.json'))

