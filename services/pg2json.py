from decimal import Decimal

import json
from datetime import date, datetime, timedelta


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        elif isinstance(o, Decimal):
            return str(o)
        elif isinstance(o, timedelta):
            return str(o)
        return json.JSONEncoder.default(self, o)


def table_to_json(conn, schema: str, table: str, output_file: str):
        cursor = conn.cursor()

        query = f"SELECT * FROM {schema}.{table};"
        cursor.execute(query)

        col_names = [desc[0] for desc in cursor.description]

        counter = 0
        data = []
        for row in cursor:
            row_dict = {col_names[i]: row[i] for i in range(len(col_names))}
            data.append(row_dict)
            counter += 1

        with open(output_file, 'w', encoding='utf8') as f:
            json.dump(data, f, cls=DateTimeEncoder, ensure_ascii=False)

        print(f'{counter} записей из таблицы {table} успешно выгружены в файл {output_file}.')

        cursor.close()


if __name__ == '__main__':
    uri = 'postgresql://sergey:AD34qec@91.222.237.198:5434/bitza'
    schema = 'public'
    table_name = 'rent_payment'
    output_file = "rent_payment.json"
    table_to_json(uri, schema, table_name, output_file)
