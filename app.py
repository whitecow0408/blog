import requests
import sqlite3
from flask import Flask, render_template, request, jsonify, g
from bs4 import BeautifulSoup

app = Flask(__name__)
DATABASE = 'search.db'
NAVER_CLIENT_ID = "3b5y0u6rjIYtPpy4DBFp"       # 본인 키 입력
NAVER_CLIENT_SECRET = "SQksyOvTQg" # 본인 키 입력

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
            chart_data.append({'rank': int(rank), 'title': title, 'artist': artist, 'image': image})
        return chart_data
    except: return []

@app.route('/')
def main_menu(): return render_template('main.html')

@app.route('/blog')
def blog(): return render_template('index.html')

@app.route('/rank')
def rank():
    data = get_db().execute('SELECT query, COUNT(query) as c FROM search_log GROUP BY query ORDER BY c DESC LIMIT 10').fetchall()
    return render_template('rank.html', rankings=data)

@app.route('/search')
def search():
    q = request.args.get('query')
    if not q: return jsonify([]), 400
    try: get_db().execute('INSERT INTO search_log (query) VALUES (?)', (q,)).connection.commit()
    except: pass
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try: return jsonify(requests.get("https://openapi.naver.com/v1/search/blog.json", headers=headers, params={"query": q + " 맛집", "display": 10, "sort": "sim"}).json().get('items', []))
    except: return jsonify([]), 500

@app.route('/melon')
def melon():
    data = get_melon_chart()
    if data:
        db = get_db()
        db.execute('DELETE FROM melon_chart')
        for s in data:
            db.execute('INSERT INTO melon_chart (rank, title, artist, image) VALUES (?,?,?,?)', (s['rank'], s['title'], s['artist'], s['image']))
        db.commit()
    return render_template('melon.html', chart_data=data)

@app.route('/melon/search')
def melon_search():
    artist = request.args.get('artist', '')
    results = get_db().execute('SELECT * FROM melon_chart WHERE artist LIKE ? ORDER BY rank ASC', (f'%{artist}%',)).fetchall()
    return render_template('melon_search.html', results=results, keyword=artist)

@app.route('/melon/share')
def melon_share():
    db = get_db()
    # 여기서 테이블이 없으면 에러가 납니다. 1단계(init_db.py)를 꼭 실행하세요.
    data = db.execute('SELECT artist, COUNT(*) as count FROM melon_chart GROUP BY artist ORDER BY count DESC').fetchall()
    
    if data:
        top10_artists = [row['artist'] for row in data[:10]]
        top10_counts = [row['count'] for row in data[:10]]
    else:
        top10_artists = []
        top10_counts = []
        
    return render_template('melon_share.html', all_data=data, labels=top10_artists, values=top10_counts)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')