import sqlite3

conn = sqlite3.connect('search.db')
cursor = conn.cursor()

# 1. 검색어 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS search_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# 2. [이게 없어서 오류가 났을 겁니다] 멜론 차트 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS melon_chart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rank INTEGER,
    title TEXT,
    artist TEXT,
    image TEXT
)
''')

print("DB 초기화 완료! 이제 오류가 안 날 겁니다.")
conn.commit()
conn.close()