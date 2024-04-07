import re

import psycopg2
import json
from datetime import datetime


def json_to_table(uri, schema, table, input_file, options: list | None = None):
    """
    Options example: ['ignore_unique_violations']
    """
    processed_records = 0
    errors = 0
    unique_violations = 0

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
                # Конвертируем datetime из строки
                if isinstance(value, str) and re.match(r'\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$', value):
                    try:
                        dt = datetime.fromisoformat(value)
                        if ':' in value and len(value) > 10:
                            # Если строка содержит время, преобразуем в 'YYYY-MM-DDTHH:MM:SS'
                            value = dt.isoformat()
                        else:
                            # В противном случае преобразуем в 'YYYY-MM-DD'
                            value = dt.date().isoformat()
                    except ValueError:
                        pass
                    values.append(value)
                else:
                    values.append(value)

            # Оборачиваем название полей в кавычки
            keys = [f'"{k}"' for k in row.keys()]  # обернул каждый ключ в двойные кавычки
            # Заполняем SQL-запрос. Заполнитель %s подставит параметры из списка значений
            query = f'INSERT INTO "{schema}"."{table}" ({", ".join(keys)}) VALUES ({", ".join(["%s"] * len(values))})'
            try:
                cursor.execute(query, values)
                conn.commit()
                processed_records += 1
            except psycopg2.errors.UniqueViolation as e:
                if options is not None and 'ignore_unique_violations' in options:
                    unique_violations += 1
                    conn.rollback()  # откатываем транзакцию
                    continue
                else:
                    print(f'UniqueViolationError:\n{query}\nvalues: {values}')
                    errors += 1
                    raise psycopg2.errors.UniqueViolation from e
            except psycopg2.errors.InFailedSqlTransaction as e:
                # Возможно unique violation
                pass
            except Exception as e:
                print(f'Error {e}\nExecuting query:\n{query}\nvalues: {values}')
                errors += 1
                break

        # Применяем изменения
        conn.commit()
        print(f"{processed_records} rows loaded into {table} from file {input_file}, {unique_violations} unique violations, {errors} errors.")

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
    input_file = "rent_payment.json"
    json_to_table(uri, schema, table_name, input_file)
