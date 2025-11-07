import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Naver 검색 API 정보 (본인의 키로 대체해야 합니다)
NAVER_CLIENT_ID = "3b5y0u6rjIYtPpy4DBFp"       # 👈 여기에 본인의 클라이언트 ID 입력
NAVER_CLIENT_SECRET = "1231" # 👈 여기에 본인의 클라이언트 시크릿 입력

# --- 라우트(Route) 정의 ---

# 1. 메인 페이지 라우트 (Hello, World!)
@app.route('/')
def hello():
    # 이제 '/'로 접속하면 Hello, World!가 나옵니다.
    return 'Hello, World!'

# 2. 맛집 검색기를 위한 '/blog' 라우트
@app.route('/blog')
def blog_search_page():
    # 이제 '/blog'로 접속하면 index.html이 렌더링됩니다.
    return render_template('index.html')

# 3. 검색 API 라우트 (이건 변경할 필요가 없습니다)
# (index.html의 JavaScript가 이 주소를 사용합니다)
@app.route('/search')
def search():
    # 프론트엔드에서 보낸 'query' 파라미터를 받습니다.
    query = request.args.get('query')
    if not query:
        return jsonify({'error': '검색어가 없습니다.'}), 400

    # Naver 블로그 검색 API URL
    url = "https://openapi.naver.com/v1/search/blog.json"
    
    # API 헤더 설정
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    
    # API 파라미터 설정 (맛집 검색을 위해 쿼리에 '맛집'을 추가하고, 10개 요청)
    params = {
        "query": query + " 맛집",
        "display": 10,  # 10개 결과
        "sort": "sim"   # 정확도순
    }

    # Naver API에 GET 요청
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() # 오류 발생 시 예외 처리
        
        # API 응답을 JSON으로 파싱
        data = response.json()
        
        # 'items' 키(블로그 리스트)가 없는 경우 빈 리스트 반환
        items = data.get('items', [])
        return jsonify(items)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

# --- 앱 실행 ---
if __name__ == '__main__':
    app.run(debug=True)