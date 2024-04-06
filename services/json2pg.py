import psycopg2
import json
from datetime import datetime


def json_to_table(uri, schema, table, input_file):
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(uri)
        cursor = conn.cursor()

        # Открываем json-файл и загружаем данные
        with open(input_file, 'r') as f:
            data = json.load(f)

        # Для каждой записи в данных
        for row in data:
            # Создаем список значений строки
            values = []
            for value in row.values():
                # Конвертируем datetime обратно из строки
                if isinstance(value, str) and (len(value.split("-")) == 3 or len(value.split(":")) >= 2):
                    try:
                        values.append(datetime.fromisoformat(value))
                    except ValueError:
                        values.append(value)
                else:
                    values.append(value)

            # Заполняем SQL-запрос. Заполнитель %s подставит параметры из списка значений
            query = f"INSERT INTO {schema}.{table} ({', '.join(row.keys())}) VALUES ({', '.join(['%s'] * len(values))})"
            cursor.execute(query, values)

        # Применяем изменения
        conn.commit()

        print(f"Данные из файла {input_file} успешно загружены в таблицу {table}.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        # Закрываем соединение
        if conn is not None:
            cursor.close()
            conn.close()


if __name__ == '__main__':
    uri = 'postgresql://postgres:postgres@localhost:5432/django_bitza'
    schema = 'public'
    table_name = 'rent_payment'
    output_file = "rent_payment.json"
    json_to_table(uri, schema, table_name, output_file)
