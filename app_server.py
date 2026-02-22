from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import re
import os
import sys
from database import init_db, save_cafes, get_cafes
import requests
from bs4 import BeautifulSoup

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "tr30Ch1tbJBqwNlv9svx")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "fsrn1wXmk3")

# 메모리 캐시 (버전 추가로 캐시 무효화)
blog_cache = {}
CACHE_VERSION = "v18"  # 캐시 버전 (일반 단어는 지역명 필수)

def get_cafe_image_from_naver(cafe_name):
    """네이버 이미지 검색 API로 카페 이미지 가져오기"""
    url = "https://openapi.naver.com/v1/search/image"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": cafe_name, "display": 1, "sort": "sim"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data['items']:
                return data['items'][0]['link']
    except:
        pass
    return None

def get_blog_image_url(blog_url):
    """블로그에서 첫 번째 이미지 URL만 추출 (다운로드 X)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://blog.naver.com/'
        }
        
        if 'm.blog.naver.com' in blog_url:
            blog_url = blog_url.replace('m.blog.naver.com', 'blog.naver.com')
        
        response = requests.get(blog_url, headers=headers, timeout=3)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        main_frame = soup.find('iframe', id='mainFrame')
        if not main_frame:
            return None
        
        actual_url = "https://blog.naver.com" + main_frame['src']
        res = requests.get(actual_url, headers=headers, timeout=3)
        content_soup = BeautifulSoup(res.text, 'html.parser')
        
        img_tags = content_soup.select('img[src*="postfiles.pstatic.net"]')
        if not img_tags:
            return None
        
        # 첫 번째 이미지 URL 반환
        img = img_tags[0]
        img_url = img.get('data-lazy-src') or img.get('src')
        return img_url
    except:
        return None

def search_naver_blog(query, display=5):
    """네이버 블로그 검색 - test_server 코드 사용"""
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": query, "display": display * 2, "sort": "sim"}  # 더 많이 가져와서 필터링
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return [item['link'] for item in data['items']]
    except:
        pass
    return []

def analyze_blog_content(cafe_name, cafe_address):
    # 캐시 확인 (버전 포함)
    cache_key = f"{CACHE_VERSION}_{cafe_name}_{cafe_address}"
    if cache_key in blog_cache:
        return blog_cache[cache_key]
    
    # 대형 카페 브랜드 리스트
    major_brands = ['대형카페','스타벅스', '투썸플레이스', '투썸', '이디야', '커피빈', '할리스', '탐앤탐스', '파스쿠찌', '엔제리너스', '디저트39']
    is_major_cafe = any(brand in cafe_name for brand in major_brands)
    
    # 휴양지 리스트 (행정구역 키워드)
    resort_areas = [
        # 강원권
        '양양군', '양양', '강릉시', '강릉', '속초시', '속초', '고성군', '고성', '삼척시', '삼척', 
        '평창군', '평창', '정선군', '정선', '홍천군', '홍천',
        # 인천/경기권
        '중구', '월미도', '영종도', '강화군', '강화', '옹진군', '옹진', '가평군', '가평', 
        '양평군', '양평', '대부도',
        # 충청권
        '태안군', '태안', '안면도', '보령시', '보령', '대천', '서천군', '서천', '단양군', '단양',
        # 전라권
        '여수시', '여수', '순천시', '순천', '신안군', '신안', '진도군', '진도', 
        '부안군', '부안', '완도군', '완도',
        # 경상권
        '경주시', '경주', '포항시', '포항', '거제시', '거제', '남해군', '남해', 
        '통영시', '통영', '울릉군', '울릉도', '영덕군', '영덕',
        # 제주권
        '제주시', '제주', '서귀포시', '서귀포'
    ]
    is_resort_area = any(area in cafe_address for area in resort_areas)
    
    # 네이버 블로그 검색 API 호출
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    
    # 대형 카페가 아니면 "카공" 키워드 추가
    if is_major_cafe:
        query = f"{cafe_name} {cafe_address}"
    else:
        query = f"{cafe_name} {cafe_address} 카공"
    
    params = {"query": query, "display": 100, "sort": "sim"}  # 30 → 50으로 증가
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=3)
        if response.status_code != 200:
            return get_empty_result()
            
        data = response.json()
        
        # 카페 키워드 추출 (개선)
        # 지역명 추출 (시/구/동 단위)
        address_parts = cafe_address.split()
        location_keyword = ""
        for part in address_parts:
            if '시' in part or '구' in part or '동' in part or '읍' in part or '면' in part:
                location_keyword = part.replace('시', '').replace('구', '').replace('동', '').replace('읍', '').replace('면', '')
                break
        
        if cafe_name.endswith('점'):
            # "스타벅스 강남점" → "스타벅스 강남"
            cafe_keyword = cafe_name.replace('카페', '').replace('커피', '').strip()
        else:
            # 일반 카페명 처리
            temp_name = cafe_name.replace('카페', '').replace('커피', '').replace('점', '').strip()
            
            # 숫자나 "24시", "무인" 같은 일반 단어 제거
            words = temp_name.split()
            meaningful_words = []
            skip_words = ['24시', '무인', '셀프', '스터디', '공부방', '독서실']
            
            for word in words:
                # 숫자로만 구성되거나 skip_words에 있으면 제외
                if not word.isdigit() and word not in skip_words:
                    meaningful_words.append(word)
            
            # 의미있는 단어가 있으면 사용, 없으면 원본 사용
            if meaningful_words:
                cafe_keyword = ' '.join(meaningful_words)
            else:
                cafe_keyword = temp_name
        
        # 일반적인 단어(2글자 이하 또는 흔한 단어)는 지역명 필수
        common_words = ['여유', '힐링', '쉼', '휴식', '행복', '사랑', '평화', '온', '숲', '바다', '하늘']
        needs_location = len(cafe_keyword) <= 2 or any(word in cafe_keyword for word in common_words)
        
        print(f"🔍 카페명: {cafe_name} → 검색 키워드: {cafe_keyword}, 지역: {location_keyword}, 지역필수: {needs_location}")
        
        # 필터링 및 키워드 분석
        filtered_urls = []
        filtered_items = []  # 제목과 설명도 함께 저장
        all_text = ""
        cafe_description = ""
        
        # 1차 필터링: 작업 키워드 포함
        work_filtered_items = []
        basic_filtered_items = []  # 카페명+지역만 포함
        
        for item in data['items']:
            title = item.get('title', '').replace('<b>', '').replace('</b>', '')
            description = item.get('description', '').replace('<b>', '').replace('</b>', '')
            combined = (title + ' ' + description).lower()
            
            # 카페 이름 포함 확인
            if cafe_keyword.lower() not in combined:
                continue
            
            # 일반적인 단어는 지역명도 필수
            if needs_location and location_keyword:
                if location_keyword.lower() not in combined:
                    continue
            
            # 카페/커피 키워드 필수 (카페가 아닌 다른 장소 제외)
            if '카페' not in combined and '커피' not in combined and 'cafe' not in combined and 'coffee' not in combined:
                continue
            
            item_data = {
                'link': item['link'],
                'title': title,
                'description': description,
                'combined': combined
            }
            
            # 작업 키워드 체크
            work_keywords = ['카공', '공부', '작업', '노트북', '조용', '집중', '넓은', '좌석', '책', '와이파이', 'wifi', '콘센트', '충전', '스터디']
            has_work_keyword = any(keyword in combined for keyword in work_keywords)
            
            if has_work_keyword:
                work_filtered_items.append(item_data)
            else:
                basic_filtered_items.append(item_data)
        
        # 2차 필터링: 작업 키워드 있는 것 우선, 부족하면 기본 필터링 추가
        # 휴양지나 대형 카페는 작업 키워드 없어도 OK
        if is_major_cafe or is_resort_area:
            final_items = work_filtered_items + basic_filtered_items
        else:
            # 작업 키워드 있는 것이 5개 미만이면 기본 필터링도 추가 (최대 20개)
            if len(work_filtered_items) < 5:
                final_items = work_filtered_items + basic_filtered_items[:20]
            else:
                final_items = work_filtered_items
        
        # 최종 결과 생성 (최대 20개)
        for item_data in final_items[:20]:
            filtered_urls.append(item_data['link'])
            filtered_items.append({
                'url': item_data['link'],
                'title': item_data['title'],
                'description': item_data['description'][:100] + '...' if len(item_data['description']) > 100 else item_data['description']
            })
            all_text += " " + item_data['title'] + " " + item_data['description']
            if not cafe_description:
                cafe_description = item_data['description'][:80] + "..." if len(item_data['description']) > 80 else item_data['description']
        
        if not filtered_urls:
            return get_empty_result()
        
        # 키워드 카운팅
        text_lower = all_text.lower()
        
        # 콘센트 점유율 (키워드 조합으로 판단)
        outlet_count = text_lower.count('콘센트') + text_lower.count('충전') + text_lower.count('플러그')
        
        # "콘센트 많아요", "콘센트 넉넉", "모든 좌석 콘센트" 등
        if ('콘센트' in text_lower or '충전' in text_lower) and \
           ('많' in text_lower or '넉넉' in text_lower or '모든' in text_lower or '전부' in text_lower or '충분' in text_lower):
            outlet_level = "모든 좌석"
        elif ('콘센트' in text_lower or '충전' in text_lower) and \
             ('반' in text_lower or '절반' in text_lower or '일부' in text_lower):
            outlet_level = "50% 정도"
        elif outlet_count >= 1:
            outlet_level = "벽면에만"
        else:
            outlet_level = "정보 없음"
        
        # 소음 레벨
        quiet_words = text_lower.count('조용') + text_lower.count('집중') + text_lower.count('독서실') + text_lower.count('차분')
        noisy_words = text_lower.count('시끄') + text_lower.count('떠들') + text_lower.count('북적') + text_lower.count('시끌')
        if quiet_words >= 5:
            noise_level = "독서실 수준"
        elif quiet_words >= 2:
            noise_level = "잔잔한 음악"
        elif noisy_words >= 3:
            noise_level = "대화 활발"
        else:
            noise_level = "보통"
        
        # 작업 적합도
        work_mentions = (text_lower.count('노트북') + text_lower.count('작업') + 
                        text_lower.count('공부') + text_lower.count('카공') + 
                        text_lower.count('스터디') + text_lower.count('업무'))
        
        work_positive = (text_lower.count('작업하기 좋') + text_lower.count('공부하기 좋') + 
                        text_lower.count('카공하기 좋') + text_lower.count('노트북 하기 좋') +
                        text_lower.count('작업 추천') + text_lower.count('공부 추천') +
                        text_lower.count('카공 추천') + text_lower.count('카공 좋'))
        
        work_negative = (text_lower.count('작업하기 안좋') + text_lower.count('작업하기 안 좋') +
                        text_lower.count('공부하기 안좋') + text_lower.count('공부하기 안 좋') +
                        text_lower.count('카공 비추') + text_lower.count('카공 안좋'))
        
        work_score = 0
        if work_positive > 0:
            work_score = 8 + (work_mentions * 0.5)
        elif work_mentions > 0:
            work_score = work_mentions * 0.5
        work_score -= work_negative * 1
        work_score = max(0, min(10, work_score))  # 0~10점 제한
        
        # 공간감 (키워드 조합으로 판단)
        space_words = text_lower.count('넓은') + text_lower.count('넓어') + text_lower.count('여유') + text_lower.count('쾌적') + text_lower.count('공간')
        cramped_words = text_lower.count('좁은') + text_lower.count('좁아') + text_lower.count('비좁')
        
        # 대형 카페는 기본적으로 넓은 편
        if is_major_cafe:
            if cramped_words >= 1:
                space_level = "좁은 편"
            else:
                space_level = "넓은 편"  # 대형 카페 기본값
        # "넓은 공간", "공간이 넓어요", "여유로운 좌석" 등
        elif ('넓' in text_lower or '여유' in text_lower or '쾌적' in text_lower) and \
           ('공간' in text_lower or '좌석' in text_lower or '매장' in text_lower):
            space_level = "매우 넓음"
        elif space_words >= 1:
            space_level = "넓은 편"
        elif cramped_words >= 1:
            space_level = "좁은 편"
        else:
            space_level = "정보 없음"
        
        # 테이블 높이
        if '높' in text_lower and '테이블' in text_lower:
            table_height = "노트북 하기 좋음"
        elif '낮' in text_lower and '테이블' in text_lower:
            table_height = "인스타 감성형"
        else:
            table_height = "정보 없음"
        
        # 이용 제한
        if '시간제한' in text_lower or '시간 제한' in text_lower:
            time_limit = "시간 제한 있음"
        elif '카공' in text_lower and ('환영' in text_lower or '추천' in text_lower):
            time_limit = "카공 환영"
        else:
            time_limit = "정보 없음"
        
        # 와이파이
        wifi_count = text_lower.count('와이파이') + text_lower.count('wifi') + text_lower.count('인터넷')
        has_wifi = wifi_count > 0
        
        # 주차
        parking_count = text_lower.count('주차')
        has_parking = parking_count > 0
        
        # 신호등 색상 (종합 점수 기반)
        # 리뷰가 없으면 회색 (대형 카페 제외)
        if len(filtered_urls) == 0:
            if is_major_cafe:
                signal_color = "yellow"  # 대형 카페는 기본 노란색
            else:
                signal_color = "gray"  # 리뷰 없음
        else:
            # 종합 점수 계산 (최대 5점)
            total_score = 0
            review_count = len(filtered_urls)
            
            # 1. 작업 적합도 (최대 2.8점)
            if work_score >= 10:
                total_score += 2.8
            elif work_score >= 8:
                total_score += 2.2
            elif work_score >= 5:
                total_score += 1.5
            elif work_score >= 2:
                total_score += 0.8
            
            # 2. 콘센트 (최대 0.4점)
            if outlet_level == "모든 좌석":
                total_score += 0.4
            elif outlet_level == "50% 정도":
                total_score += 0.28
            elif outlet_level == "벽면에만":
                total_score += 0.2
            
            # 3. 소음 레벨 (최대 0.3점)
            if noise_level == "독서실 수준":
                total_score += 0.3
            elif noise_level == "잔잔한 음악":
                total_score += 0.21
            elif noise_level == "보통":
                total_score += 0.15
            
            # 4. 공간감 (최대 0.8점)
            if space_level == "매우 넓음":
                total_score += 0.8
            elif space_level == "넓은 편":
                total_score += 0.5
            
            # 5. WiFi (최대 0.4점)
            if has_wifi:
                total_score += 0.4
            
            # 6. 리뷰 개수 (최대 0.3점)
            if review_count >= 15:
                total_score += 0.3
            elif review_count >= 10:
                total_score += 0.23
            elif review_count >= 5:
                total_score += 0.15
            
            # 대형 카페는 최소 2.5점 보장
            if is_major_cafe and total_score < 2.5:
                total_score = 2.5
            
            # 휴양지 보너스 +1점
            if is_resort_area:
                total_score += 1
            
            # 대형 카페 보너스 +1점
            if is_major_cafe:
                total_score += 1
            
            # 최대 5점 제한
            total_score = min(5.0, total_score)
            
            # 신호등 색상 결정
            if total_score >= 3.7:
                signal_color = "green"
            elif total_score >= 2.5:
                signal_color = "yellow"
            else:
                signal_color = "red"
        
        # 키워드 빈도 분석
        keywords = {}
        keyword_list = ['노트북', '작업', '공부', '카공', '조용', '집중', '넓은', '좌석', '콘센트', '충전', '와이파이', 'wifi']
        for keyword in keyword_list:
            count = text_lower.count(keyword)
            if count > 0:
                keywords[keyword] = count
        
        result = {
            "workScore": round(work_score, 1),
            "outletLevel": outlet_level,
            "noiseLevel": noise_level,
            "spaceLevel": space_level,
            "tableHeight": table_height,
            "timeLimit": time_limit,
            "hasWifi": has_wifi,
            "hasParking": has_parking,
            "signalColor": signal_color,
            "blogCount": len(filtered_urls),
            "blogUrls": filtered_urls,
            "blogItems": filtered_items,
            "description": cafe_description,
            "keywords": keywords,
            "totalScore": round(total_score, 1) if len(filtered_urls) > 0 else 0
        }
        
        blog_cache[cache_key] = result
        return result
        
    except Exception as e:
        print(f"Error analyzing blog: {e}")
        return get_empty_result()

def get_empty_result():
    return {
        "workScore": 0,
        "outletLevel": "정보 없음",
        "noiseLevel": "정보 없음",
        "spaceLevel": "정보 없음",
        "tableHeight": "정보 없음",
        "timeLimit": "정보 없음",
        "hasWifi": False,
        "hasParking": False,
        "signalColor": "gray",
        "blogCount": 0,
        "blogUrls": [],
        "blogItems": [],
        "description": "",
        "keywords": {},
        "totalScore": 0
    }

class Handler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/blog-search':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            cafe_name = data.get('name', '')
            cafe_address = data.get('address', '')
            
            result = analyze_blog_content(cafe_name, cafe_address)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/api/clear-cache':
            global blog_cache
            blog_cache.clear()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "message": "Cache cleared"}).encode('utf-8'))
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    print("🚀 Venue app running at http://localhost:5000")
    print("📊 Database: venue.db")
    print("🔄 Refresh data: http://localhost:5000/api/refresh")
    HTTPServer(('', 5000), Handler).serve_forever()
