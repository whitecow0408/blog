import sqlite3

conn = sqlite3.connect('search.db')
cursor = conn.cursor()

# 1. 기존 검색어 저장 테이블 (이미 있으면 건너뜀)
cursor.execute('''
CREATE TABLE IF NOT EXISTS search_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# 2. (NEW) 멜론 차트 저장 테이블
# 순위, 제목, 가수, 이미지 주소를 저장합니다.
cursor.execute('''
CREATE TABLE IF NOT EXISTS melon_chart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rank INTEGER,
    title TEXT,
    artist TEXT,
    image TEXT
)
''')

print("데이터베이스 초기화 완료: 'search_log'와 'melon_chart' 테이블이 준비되었습니다.")

conn.commit()
conn.close()