import requests
import sqlite3
from flask import Flask, render_template, request, jsonify, g
from bs4 import BeautifulSoup

# 1. 앱 생성
app = Flask(__name__)

# --- 설정 및 API 키 ---
DATABASE = 'search.db'

# [중요] 본인의 네이버 API 키를 여기에 넣으세요!
NAVER_CLIENT_ID = "3b5y0u6rjIYtPpy4DBFp"
NAVER_CLIENT_SECRET = "SQksyOvTQg"

# --- DB 관련 함수 ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- 멜론 크롤링 함수 ---
def get_melon_chart():
    url = "https://www.melon.com/chart/index.htm"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        songs = soup.select('.lst50, .lst100')
        
        chart_data = []
        for song in songs:
            rank = song.select_one('.rank').text
            title = song.select_one('.ellipsis.rank01 a').text
            artist = song.select_one('.ellipsis.rank02 a').text
            image = song.select_one('.image_typeAll img')['src']
            
            chart_data.append({
                'rank': int(rank),
                'title': title,
                'artist': artist,
                'image': image
            })
        return chart_data
    except Exception as e:
        print(f"크롤링 오류: {e}")
        return []

# --- 라우트 정의 ---

# 1. (NEW) 메인 메뉴 페이지
@app.route('/')
def main_menu():
    return render_template('main.html')

# 2. 맛집 검색 페이지 (기존)
@app.route('/blog')
def blog_search_page():
    return render_template('index.html')

# 3. 맛집 검색 API (기존)
@app.route('/search')
def search():
    query = request.args.get('query')
    if not query: return jsonify([]), 400

    # DB 저장
    try:
        db = get_db()
        db.execute('INSERT INTO search_log (query) VALUES (?)', (query,))
        db.commit()
    except: pass

    # 네이버 API 호출
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query + " 맛집", "display": 10, "sort": "sim"}
    
    try:
        res = requests.get(url, headers=headers, params=params)
        return jsonify(res.json().get('items', []))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 4. 인기 검색어 랭킹 (기존)
@app.route('/rank')
def rank():
    db = get_db()
    cursor = db.execute('SELECT query, COUNT(query) as count FROM search_log GROUP BY query ORDER BY count DESC LIMIT 10')
    return render_template('rank.html', rankings=cursor.fetchall())

# 5. (UPDATE) 멜론 차트 + DB 저장
@app.route('/melon')
def melon():
    # 1. 크롤링으로 최신 데이터 가져오기
    data = get_melon_chart()
    
    # 2. DB에 저장 (기존 데이터 지우고 최신 데이터로 갱신)
    if data:
        db = get_db()
        db.execute('DELETE FROM melon_chart') # 기존 차트 삭제
        for song in data:
            db.execute('INSERT INTO melon_chart (rank, title, artist, image) VALUES (?, ?, ?, ?)',
                       (song['rank'], song['title'], song['artist'], song['image']))
        db.commit()
        
    return render_template('melon.html', chart_data=data)

# 6. (NEW) 가수 검색 기능
@app.route('/melon/search')
def melon_artist_search():
    artist_query = request.args.get('artist') # 검색창에서 보낸 가수 이름
    db = get_db()
    
    # LIKE를 사용해서 가수가 포함된 모든 노래 찾기
    cursor = db.execute('SELECT * FROM melon_chart WHERE artist LIKE ? ORDER BY rank ASC', (f'%{artist_query}%',))
    results = cursor.fetchall()
    
    return render_template('melon_search.html', results=results, keyword=artist_query)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')