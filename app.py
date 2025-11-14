import requests
import sqlite3  # <--- NEW: SQLite3 임포트
from flask import Flask, render_template, request, jsonify, g # <--- NEW: g 임포트

app = Flask(__name__)

# --- NEW: SQLite 설정 ---
DATABASE = 'search.db' # 1단계에서 생성한 DB 파일

def get_db():
    """DB에 연결하고, 연결 객체를 g에 저장합니다."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # 딕셔너리처럼 열 이름으로 결과에 접근할 수 있게 설정
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception):
    """요청이 끝나면 DB 연결을 자동으로 닫습니다."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
# --- END: SQLite 설정 ---


# Naver 검색 API 정보
NAVER_CLIENT_ID = "3b5y0u6rjIYtPpy4DBFp"
NAVER_CLIENT_SECRET = "SQksyOvTQg"

# --- 라우트(Route) 정의 ---

# 1. 메인 페이지 라우트 (Hello, World!)
@app.route('/')
def hello():
    return 'Hello, World!'

# 2. 맛집 검색기를 위한 '/blog' 라우트
@app.route('/blog')
def blog_search_page():
    return render_template('index.html')

# 3. 검색 API 라우트 (검색어 저장 기능 추가됨)
@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': '검색어가 없습니다.'}), 400

    # --- NEW: 검색어 데이터베이스에 저장 ---
    try:
        db = get_db()
        # 사용자가 입력한 검색어를 그대로 저장 (예: '해운대 파스타')
        db.execute('INSERT INTO search_log (query) VALUES (?)', (query,))
        db.commit() # 변경사항 저장
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        # DB 오류가 발생해도 검색 기능 자체는 동작하도록 함
    # --- END: 검색어 저장 ---

    # Naver 블로그 검색 API URL
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query + " 맛집",
        "display": 10,
        "sort": "sim"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get('items', [])
        return jsonify(items)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

# 4. --- NEW: 인기 검색어 랭킹 페이지 ---
@app.route('/rank')
def rank():
    db = get_db()
    
    # 쿼리: search_log 테이블에서
    # query를 기준으로 그룹화(GROUP BY)하고,
    # 각 그룹의 개수(COUNT)를 세고 ('count'라는 별명으로)
    # 개수가 많은 순(DESC)으로 정렬(ORDER BY)하여
    # 상위 10개(LIMIT 10)를 가져옵니다.
    cursor = db.execute('''
        SELECT query, COUNT(query) as count 
        FROM search_log 
        GROUP BY query 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    
    rankings = cursor.fetchall() # 모든 결과(상위 10개)를 가져옴
    
    # 'rank.html' 템플릿에 'rankings' 데이터를 넘겨주며 렌더링
    return render_template('rank.html', rankings=rankings)
# --- END: 랭킹 페이지 ---


# --- 앱 실행 ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')