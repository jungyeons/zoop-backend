#  Naver Real Estate Crawler System

네이버 부동산 API를 활용하여 단지 정보, 매물 정보, 공인중개사 정보를 수집하고 통합 데이터셋을 생성하는 **크롤링 시스템**입니다.

---

##  1. 시스템 개요

이 시스템은 다음과 같은 기능을 제공합니다:

- 지역별 단지 목록 수집
- 단지별 매물 정보 수집 (페이지네이션 포함)
- 공인중개사 정보 수집 및 통합
- JSON 기반의 결과 저장
- 향후 DB 연동 및 병렬 처리 확장 가능

---

##  2. 데이터 수집 프로세스

### 2.1 전체 프로세스 흐름

1. **지역별 단지 목록 수집**
2. **단지별 매물 정보 수집**
3. **공인중개사 정보 수집 및 데이터 결합**
4. **최종 통합 데이터셋 생성**

### 2.2 상세 프로세스

####  단지 목록 수집

- 지역 코드(`cortarNo`)를 기반으로 단지 정보 조회  
- `complex_list_{city}_{district}_{timestamp}.json` 형태로 저장

####  매물 정보 수집

- 단지 번호 기준 매물 조회
- 페이지 단위로 반복 수집
- `naver_land_structured_*.json`, `naver_land_flattened_*.json` 으로 저장

####  공인중개사 정보 수집

- 별도 API에서 중개사 정보 조회 후 결합

---

##  3. API 명세

### 3.1  단지 목록 조회

| 항목      | 설명 |
|-----------|------|
| 엔드포인트 | `/api/regions/complexes` |
| 메서드     | `GET` |
| 파라미터   | `cortarNo`, `realEstateType=APT`, `order=rank` |
| 응답      | 단지 목록 리스트 |

---

### 3.2  매물 목록 조회

| 항목      | 설명 |
|-----------|------|
| 엔드포인트 | `/api/articles/complex/{complex_no}` |
| 메서드     | `GET` |
| 파라미터   | `complexNo`, `realEstateType=APT`, `tradeType=A1`, `page`, `type=list`, `order=rank` |
| 응답      | 매물 목록 리스트 |

---

### 3.3  매물 상세 정보

| 항목      | 설명 |
|-----------|------|
| 엔드포인트 | `/api/articles/{article_no}` |
| 메서드     | `GET` |
| 파라미터   | `articleNo`, `complexNo` |
| 응답      | 매물 상세 JSON |

---

### 3.4  단지 정보

| 항목      | 설명 |
|-----------|------|
| 엔드포인트 | `/api/complexes/{complex_no}` |
| 메서드     | `GET` |
| 파라미터   | `complexNo` |
| 응답      | 단지 상세 정보 |

---

##  4. 데이터 구조

### 4.1 단지 목록 (`complex_list_*.json`)

```json
{
  "city": "서울특별시",
  "district": "마포구",
  "timestamp": "YYYYMMDD_HHMMSS",
  "total_complexes": 123,
  "dong_complexes": {
    "동이름": [
      {
        "complexNo": "단지번호",
        "complexName": "단지이름"
      }
    ]
  }
}
```
---

### 4.2 매물 상세 정보
```json
{
  "complexInfo": {
    "complexNo": "단지번호",
    "complexName": "단지이름"
  },
  "articleList": [
    {
      "articleNo": "매물번호",
      "articleName": "매물이름",
      "tradeType": "거래유형"
    }
  ]
}
```
---

### 5. 사용 방법


#### 5-1. 실행 명령어 
- python realestate_complex_scraper.py
- python realestate_details_fetcher.py

---

#### 5-2. 주요 설정
- 지역 설정: city, district 변수 수정
- 수집 제한: max_pages 설정 가능
- 딜레이 설정: time.sleep() 조절

---
#### 5-3. 출력 파일
- complex_list_*.json	단지 목록
- naver_land_structured_*.json	구조화된 매물 정보
- naver_land_flattened_*.json	평탄화된 매물 리스트
  
---

### 6. 주의 사항

#### 6-1. API 딜레이 설정 
- time.sleep(random.uniform(0.17, 0.33))  # 단지별
- time.sleep(random.uniform(0.02, 0.04))  # 페이지별
- time.sleep(random.uniform(3, 5))        # 인증 API
 
---

 
#### 6-2. 인증 정보 관리
- HEADERS: Authorization, User-Agent 포함
- COOKIES: NID_AUT, NNB 등 포함
- 갱신 필요 시, 브라우저 F12 → 네트워크 탭 → 값 추출

---



#### 6-3. 재시도 및 에러 처리
```json
retry_count = 0
while retry_count < max_retries:
    try:
        # 요청
    except:
        retry_count += 1
        time.sleep(2)
```


---

#### 6-4. 백업 및 파일 저장
파일명에 timestamp 포함
단지별, 전체 결과 JSON 저장


---


### 7. 에러 처리 전략
#### 7-1. API 실패 시 재시도
최대 3회 재시도
상태코드 확인 (401, 403, 500 등)


---


#### 7-2. 인증 만료 시 안내
 인증 실패: 세션 만료
 브라우저 로그인 후 F12 → 쿠키/토큰 복사 필요


---


#### 7-3. 데이터 유효성 검증
- 필수 필드 누락 여부 확인
- 데이터 타입 일치 여부 확인
- 중복 체크 및 범위 체크 수행

---

### 스크린샷

 <img width="1918" height="918" alt="image" src="https://github.com/user-attachments/assets/cb029c68-aad9-40b1-8def-c5bdf2d91380" />

 
<img width="1355" height="311" alt="image" src="https://github.com/user-attachments/assets/eb9aebd0-b630-49b9-bca5-07f5fc34c0f0" />

<img width="833" height="862" alt="image" src="https://github.com/user-attachments/assets/13659d53-832c-4d9b-84a2-e8e3369b8912" />




