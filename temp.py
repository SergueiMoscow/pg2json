import json
import os
import logging
import psycopg2
import datetime
from services.utils import get_db_config
from psycopg2.extras import RealDictCursor
from dateutil import parser

logger = logging.getLogger(__name__)
logging.basicConfig(filename='compare.log', level=logging.INFO)


def compare(app: str, db: str, table: str, backup_path: str):
    db_config = get_db_config(app, db)
    json_file = os.path.join(backup_path, f'{table}.json')
    conn = psycopg2.connect(db_config['dsn'])
    schema = db_config['schema']
    with open(json_file, 'r') as f:
        data = json.load(f)

    for row in data:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = 'SELECT * from %s.%s where id=%d' % (schema, table, row['id'])
        try:
            cursor.execute(query)
            result = cursor.fetchone()
        except Exception as e:
            pass
        else:
            for k, v in row.items():
                if result is None:
                    logger.info(f"Id: {row['id']} not exists in db")
                    break
                if isinstance(result[k], datetime.datetime):
                    real_value = parser.parse(v)
                elif isinstance(result[k], datetime.date):
                    real_value = parser.parse(v).date()
                else:
                    real_value = v
                if result[k] != real_value:
                    logger.info(f"Id: {row['id']} field: {k} db: {result[k]}, json: {v}")


compare(
    app='bitza',
    db='local',
    table='rent_payment',
    backup_path='/home/sergey/DB_Backups/bitza/local/2024-04-05',
)

