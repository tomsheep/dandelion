SQLITE_SETTINGS = {
    'dbn': 'sqlite',
    'schema': 'schema-sqlite3.sql',
    'config': {
        'db': 'blog.db'
    }
}

MYSQL_SETTINGS = {
    'dbn': 'mysql',
    'schema': 'schema-mysql.sql',
    'config': {
        'host': '127.0.0.1',
        'user': 'root',
        'pw': 'admin@dev',
        'port': 3306,
        'db': 'blog'
    }
}

DB_SETTINGS = SQLITE_SETTINGS
# DB_SETTINGS = MYSQL_SETTINGS
