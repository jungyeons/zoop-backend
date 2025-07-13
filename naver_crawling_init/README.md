1. 시스템 개요
이 시스템은 네이버 부동산의 단지 정보, 매물 정보, 공인중개사 정보를 수집하여 통합 데이터셋을 생성하는 크롤링 시스템입니다.


2. 데이터 수집 프로세스
2.1 전체 프로세스 흐름
1. 지역별 단지 목록 수집
2. 수집된 단지별 매물 정보 수집
3. 공인중개사 정보 수집 및 데이터 결합
4. 최종 데이터셋 생성

2.2 상세 프로세스단지 목록 수집
1. 지역 코드(cortarNo)를 기준으로 해당 지역의 모든 단지 정보 수집
2. 수집된 데이터는 JSON 파일로 저장 (complex_list_{city}_{district}_{timestamp}.json)
3. 매물 정보 수집
4. 단지 목록을 기준으로 각 단지별 매물 정보 수집
5. 페이지네이션을 통한 전체 매물 데이터 수집
6. 수집된 데이터는 단지별로 JSON 파일로 저장
7. 공인중개사 정보 수집
8. 별도 API를 통한 공인중개사 정보 수집
9. 기존 매물 데이터와 결합

3. API 명세

3.1 단지 목록 조회
 

- 엔드포인트: /api/regions/complexes
- 메소드: GET
- 파라미터:
- cortarNo: 지역 코드 (예: 마포구 1144000000)
- realEstateType: APT
- order: rank
- 응답: 단지 목록 정보

3.2 매물 목록 조회
 

- 엔드포인트: /api/articles/complex/{complex_no}
- 메소드: GET
- 파라미터:
- complexNo: 단지 번호
- realEstateType: APT
- tradeType: A1 (매매)
- page: 페이지 번호
- type: list
- order: rank
- 응답: 매물 목록 정보

3.3 매물 상세 정보
- 엔드포인트: /api/articles/{article_no}
- 메소드: GET
- 파라미터:
- articleNo: 매물 번호
- complexNo: 단지 번호
- 응답: 매물 상세 정보

3.4 단지 정보
- 엔드포인트: /api/complexes/{complex_no}
- 메소드: GET
- 파라미터:
- complexNo: 단지 번호
- 응답: 단지 상세 정보

4. 데이터 구조

4.1 단지 목록 데이터
{
  "city": "서울특별시",
  "district": "마포구",
  "timestamp": "YYYYMMDD_HHMMSS",
  "total_complexes": 123,
  "dong_complexes": {
    "동이름": [
      {
        "complexNo": "단지번호",
        "complexName": "단지이름",
        ...
      }
    ]
  }
}​
 


4.2 매물 데이터
{
  "complexInfo": {
    "complexNo": "단지번호",
    "complexName": "단지이름",
    ...
  },
  "articleList": [
    {
      "articleNo": "매물번호",
      "articleName": "매물이름",
      "tradeType": "거래유형",
      ...
    }
  ]
}​

5. 사용 방법

5.1 실행 방법

- python a1.py


5.2 주요 설정
- 지역 설정: city와 district 변수 수정
- 수집 제한: max_pages 파라미터로 페이지 수 제한 가능
- 딜레이 설정: API 호출 간 딜레이 조정 가능

5.3 출력 파일
- 단지 목록: complex_list_{city}_{district}_{timestamp}.json
- 매물 정보: naver_land_structured_{city}_{district}_{timestamp}.json
- 평탄화된 매물 정보: naver_land_flattened_{city}_{district}_{timestamp}.json

6. 주의사항
- API 호출 시 적절한 딜레이 필요 (서버 부하 방지)
- 인증 토큰 및 쿠키 관리 필요
- 에러 처리 및 재시도 로직 구현
- 데이터 백업 및 저장 관리

6-1. API 호출 시 적절한 딜레이 필요 
# 현재 코드에서 구현된 딜레이 예시
time.sleep(random.uniform(0.17, 0.33))  # 단지별 딜레이
time.sleep(random.uniform(0.02, 0.04))  # 페이지별 딜레이
time.sleep(random.uniform(3, 5))        # API 호출 간 딜레이
목적: 서버에 과도한 부하를 주지 않기 위함
구현 방법:
랜덤한 시간 간격으로 딜레이 설정
API 호출 유형별로 다른 딜레이 적용
서버 응답 시간을 고려한 적절한 간격 설정

 

6-2. 인증 토큰 및 쿠키 관리 
# 현재 코드에서 사용 중인 인증 정보
HEADERS = {
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user-agent": "Mozilla/5.0...",
    ...
}

COOKIES = {
    "NNB": "ETKDTVXNDWQGO",
    "NID_AUT": "K4mFgwh4iFNwaWRcmCWJyvLbLrtmvvnOiUTPIwSurQeOeqviQIo7/XbIsd/TMWZ9",
    ...
}
 

목적: API 접근 권한 유지
관리 방법:
토큰 만료 시간 모니터링
세션 유지 및 갱신
쿠키 값 정기적 업데이트

 

6-3. 에러 처리 및 재시도 로직 
def get_article_details(article_no, session, max_retries=3):
    retry_count = 0
    while retry_count < max_retries:
        try:
            # API 호출 로직
            if response.status_code == 200:
                return response.json()
            else:
                retry_count += 1
                time.sleep(2)
        except Exception as e:
            retry_count += 1
            time.sleep(2)
목적: 안정적인 데이터 수집 보장
구현 방법:
예외 상황별 처리 로직 구현
재시도 횟수 제한 설정
실패 시 대기 시간 설정

 

6-4. 데이터 백업 및 저장 관리 
# 현재 코드에서의 데이터 저장 예시
output_filename = f'complex_details_{data["district"]}_all_{result_data["timestamp"]}.json'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(result_data, f, ensure_ascii=False, indent=2)
목적: 데이터 손실 방지 및 복구 가능성 확보
관리 방법:
정기적인 백업 수행
타임스탬프를 포함한 파일명 사용
데이터 저장 형식 표준화

 

7. 에러 처리
- API 호출 실패 시 최대 3회 재시도
- 세션 만료 시 새로운 세션 생성
- 응답 데이터 유효성 검증
 
7-1. API 호출 실패 시 재시도 
def get_complex_info(complex_no, session, max_retries=3):
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = session.get(complex_info_url, headers=complex_headers, cookies=COOKIES)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 단지 정보 요청 실패: {response.status_code}")
                retry_count += 1
                time.sleep(2)
HTTP 상태 코드 확인
실패 시 대기 시간 후 재시도
최대 재시도 횟수 제한

 
7-2. 세션 만료 처리 
if response.status_code == 401:
    print("❌ 인증 실패: 세션이 만료되었거나 유효하지 않습니다.")
    print("💡 해결방법: 브라우저에서 네이버 부동산에 로그인하고 F12 > 네트워크에서 다음 정보를 복사해주세요:")
    print("1. NID_AUT 쿠키 값")
    print("2. Authorization 헤더 값")
401 상태 코드 확인
새로운 세션 생성
인증 정보 갱신

 
7-3. 응답 데이터 유효성 검증 
def process_complex_list(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 데이터 구조 검증
        if not all(key in data for key in ['city', 'district', 'dong_complexes']):
            raise ValueError("필수 데이터 필드가 누락되었습니다.")
            
        # 데이터 타입 검증
        if not isinstance(data['dong_complexes'], dict):
            raise TypeError("dong_complexes는 딕셔너리 타입이어야 합니다.")
검증 항목:
필수 필드 존재 여부
데이터 타입 확인
값의 범위 및 형식 검증
중복 데이터 확인


8. 향후 개선 사항
- 병렬 처리 도입으로 수집 속도 개선
- 데이터베이스 연동
- 실시간 모니터링 시스템 구축
- API 응답 캐싱 구현
 

 

 
8-1. 병렬 처리 도입으로 수집 속도 개선 
# 현재 코드 (순차 처리)
for complex_no in complex_numbers:
    result = crawl_complex(complex_no)
    all_data[str(complex_no)] = result

# 개선 방안 (병렬 처리 예시)
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_crawl(complex_numbers, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_complex = {
            executor.submit(crawl_complex, complex_no): complex_no 
            for complex_no in complex_numbers
        }
        
        for future in as_completed(future_to_complex):
            complex_no = future_to_complex[future]
            try:
                result = future.result()
                all_data[str(complex_no)] = result
            except Exception as e:
                print(f"Error processing complex {complex_no}: {e}")
 

개선 포인트:
ThreadPoolExecutor를 사용한 동시 처리
적절한 worker 수 설정으로 리소스 관리
각 단지별 독립적인 크롤링 수행
진행 상황 모니터링 기능 추가

 

 

8-2. 데이터베이스 연동 
# 데이터베이스 연동 예시 (SQLAlchemy 사용)
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Complex(Base):
    __tablename__ = 'complexes'
    
    id = Column(Integer, primary_key=True)
    complex_no = Column(String, unique=True)
    complex_name = Column(String)
    created_at = Column(DateTime)
    
class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    article_no = Column(String, unique=True)
    complex_no = Column(String)
    price = Column(Integer)
    created_at = Column(DateTime)

# 데이터베이스 연결 및 저장
def save_to_database(data):
    engine = create_engine('postgresql://user:password@localhost/realestate')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        for complex_data in data['complexes']:
            complex = Complex(
                complex_no=complex_data['complexNo'],
                complex_name=complex_data['complexName'],
                created_at=datetime.now()
            )
            session.add(complex)
            
            for article in complex_data['articles']:
                article_db = Article(
                    article_no=article['articleNo'],
                    complex_no=complex_data['complexNo'],
                    price=article['price'],
                    created_at=datetime.now()
                )
                session.add(article_db)
                
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
 

 

개선 포인트:
관계형 데이터베이스 사용 (PostgreSQL 등)
데이터 모델 정의 및 스키마 설계
트랜잭션 관리 및 에러 처리
데이터 정합성 보장

 

 

8-3. 실시간 모니터링 시스템 구축 
# 모니터링 시스템 예시
from prometheus_client import start_http_server, Counter, Gauge
import time

# 메트릭 정의
CRAWL_REQUESTS = Counter('crawl_requests_total', 'Total number of crawl requests')
CRAWL_ERRORS = Counter('crawl_errors_total', 'Total number of crawl errors')
CRAWL_DURATION = Gauge('crawl_duration_seconds', 'Time spent crawling')

def monitor_crawl():
    start_time = time.time()
    try:
        # 크롤링 로직
        CRAWL_REQUESTS.inc()
        # ... 크롤링 수행 ...
    except Exception as e:
        CRAWL_ERRORS.inc()
        raise e
    finally:
        CRAWL_DURATION.set(time.time() - start_time)

# 모니터링 서버 시작
start_http_server(8000)
 


개선 포인트:
Prometheus를 사용한 메트릭 수집
Grafana를 통한 대시보드 구성
알림 시스템 구축
성능 지표 모니터링

 

 

8-4. API 응답 캐싱 구현 
# 캐싱 구현 예시 (Redis 사용)
import redis
from functools import lru_cache
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_complex_info(complex_no):
    # Redis에서 캐시 확인
    cached_data = redis_client.get(f"complex:{complex_no}")
    if cached_data:
        return json.loads(cached_data)
    
    # 캐시가 없는 경우 API 호출
    data = get_complex_info(complex_no)
    
    # Redis에 캐시 저장 (1시간)
    redis_client.setex(
        f"complex:{complex_no}",
        3600,  # TTL: 1시간
        json.dumps(data)
    )
    return data

# 메모리 캐시 사용 예시
@lru_cache(maxsize=1000)
def get_article_details(article_no):
    # 기존 로직
    pass
 



 <img width="1918" height="918" alt="image" src="https://github.com/user-attachments/assets/cb029c68-aad9-40b1-8def-c5bdf2d91380" />

 
<img width="1355" height="311" alt="image" src="https://github.com/user-attachments/assets/eb9aebd0-b630-49b9-bca5-07f5fc34c0f0" />

<img width="833" height="862" alt="image" src="https://github.com/user-attachments/assets/13659d53-832c-4d9b-84a2-e8e3369b8912" />




