import sqlite3

# 'search.db'라는 이름의 데이터베이스 파일을 생성합니다.
conn = sqlite3.connect('search.db')
cursor = conn.cursor()

# 'search_log'라는 테이블을 생성합니다.
# id: 고유 번호
# query: 검색어
# timestamp: 검색 시간 (자동 생성)
cursor.execute('''
CREATE TABLE IF NOT EXISTS search_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

print("Database 'search.db' and table 'search_log' created successfully.")

conn.commit()
conn.close()