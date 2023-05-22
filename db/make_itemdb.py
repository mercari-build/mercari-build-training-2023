import sqlite3

path="mercari.sqlite3"
create_table1="""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category_id INT,
    image_name TEXT
);
"""
create_table2="""
CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY,
    name TEXT
);
"""

#dbに接続
conn=sqlite3.connect(path)
cursor=conn.cursor()

#テーブル作成
cursor.execute(create_table1)
cursor.execute(create_table2)

#スキーマを保存
with open("items.db", "w") as f:
    f.write(create_table1)
    f.write(create_table2)

conn.close()

