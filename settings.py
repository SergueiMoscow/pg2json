import psycopg2
from environs import Env

env = Env()
env.read_env()

dsn = env('DB_DSN')
backup_dir = env('BACKUP_DIR')
schema = env('SCHEMA')

applications = {

}