import sqlite3

path="mercari.sqlite3"
create_table="""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    image_name TEXT
);
"""

#dbに接続
conn=sqlite3.connect(path)
cursor=conn.cursor()

#テーブル作成
cursor.execute(create_table)

#スキーマを保存
with open("items.db", "w") as f:
    f.write(create_table)

conn.close()
