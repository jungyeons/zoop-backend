import requests
import json
import time
import random
from datetime import datetime

#  최신 인증 정보
headers = {
    #  비공개
}

cookies = {
   #  비공개
}

def get_complex_list_by_dong(city='서울특별시', district='마포구'):
    """지역구의 단지 목록을 가져오는 함수"""
    # 마포구의 cortarNo: 1144000000
    url = f"비공개cortarNo=1144000000"
    
    try:
        # 먼저 지역 정보 가져오기
        res = requests.get(url, headers=headers, cookies=cookies)
        res.raise_for_status()
        region_data = res.json()
        
        # 동네 목록 가져오기
        dong_list = region_data.get('regionList', [])
        if not dong_list:
            print("⚠ 동네 목록을 가져오지 못했습니다.")
            return []
            
        print(f" {city} {district}의 동네 목록:")
        for dong in dong_list:
            print(f"  - {dong['cortarName']} (코드: {dong['cortarNo']})")
        
        # 각 동네별로 단지 목록 가져오기
        all_complexes = []
        dong_complexes = {}  # 동네별 단지 목록 저장
        
        for dong in dong_list:
            dong_no = dong['cortarNo']
            dong_name = dong['cortarName']
            print(f"\n {dong_name} 단지 목록 가져오는 중...")
            
            complex_url = f"비공개{dong_no}&비공개"
            complex_res = requests.get(complex_url, headers=headers, cookies=cookies)
            complex_res.raise_for_status()
            data = complex_res.json()
            
            complexes = data.get('complexList', [])
            if complexes:
                print(f" {dong_name}에서 {len(complexes)}개 단지 발견!")
                all_complexes.extend(complexes)
                dong_complexes[dong_name] = complexes  # 동네별 단지 목록 저장
            else:
                print(f" {dong_name}에는 단지가 없습니다.")
            
            time.sleep(1)  # API 호출 간 딜레이
        
        if not all_complexes:
            print(" 전체 동네에서 단지를 찾지 못했습니다.")
            return []
            
        print(f"\n 총 {len(all_complexes)}개 단지 발견!")
        
        # 단지 목록을 JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        complex_list_filename = f'complex_list_{city}_{district}_{timestamp}.json'
        
        # 저장할 데이터 구조화
        save_data = {
            "city": city,
            "district": district,
            "timestamp": timestamp,
            "total_complexes": len(all_complexes),
            "dong_complexes": dong_complexes,  # 동네별 단지 목록
            "all_complexes": all_complexes  # 전체 단지 목록
        }
        
        with open(complex_list_filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        print(f"\n 단지 목록이 {complex_list_filename}에 저장되었습니다.")
        
        return [c['complexNo'] for c in all_complexes]
        
    except Exception as e:
        print(f" 단지 목록 가져오기 실패: {str(e)}")
        if hasattr(e, 'response'):
            print(f"응답 상태 코드: {e.response.status_code}")
            print(f"응답 내용: {e.response.text[:200]}...")
        return []

def crawl_complex(complex_no, max_pages=20):
    """단지 전체 매물과 isMoreData 등 전체 응답을 그대로 합쳐 반환"""
    combined_result = {
        "isMoreData": False,
        "articleList": [],
        "mapExposedCount": 0,
        "nonMapExposedIncluded": False
    }

    page = 1
    total_pages = 1

    while page <= total_pages:
        # 단순화된 URL 사용 (필수 파라미터만 포함)
        url = (
            f'비공개{complex_no}'
            f'?realEstateType=비공개&tradeType=비공개&page={page}'
            f'&complexNo={complex_no}&type=list&order=rank'
        )
        
        try:
            print(f"\n API 요청 URL: {url}")
            
            # 세션 객체 생성
            session = requests.Session()
            
            # 단지 페이지 먼저 접근 (세션 생성)
            complex_page_url = f'비공개{complex_no}'
            session.get(complex_page_url, headers=headers, cookies=cookies)
            
            # Authorization 토큰 가져오기
            auth_url = f'비공개{complex_no}'
            auth_response = session.get(auth_url, headers=headers, cookies=cookies)
            auth_token = auth_response.headers.get('authorization', '')
            
            # Referer 헤더를 해당 단지로 변경 (더 구체적인 URL 사용)
            dynamic_headers = headers.copy()
            dynamic_headers['referer'] = f'비공개{complex_no}?비공개'
            if auth_token:
                dynamic_headers['authorization'] = auth_token
            
            # 랜덤 시간 딜레이 추가 (3-5초)
            random_sec = random.uniform(3, 5)
            print(f"⏳ {random_sec:.2f}초 대기 중...")
            time.sleep(random_sec)
            
            # API 요청 (동적 헤더 사용)
            response = session.get(url, headers=dynamic_headers, cookies=cookies)
            
            if response.status_code == 401:
                print(f" 단지 {complex_no}의 {page}페이지 인증 실패")
                print("현재 쿠키 상태:")
                for cookie_name, cookie_value in cookies.items():
                    if cookie_value:
                        print(f"  - {cookie_name}: {'있음'}")
                    else:
                        print(f"  - {cookie_name}: {'없음'}")
                break

            if response.status_code != 200:
                print(f" 단지 {complex_no}의 {page}페이지 요청 실패: {response.status_code}")
                print(f"응답 내용: {response.text[:500]}...")
                break

            data = response.json()
            print(f" API 응답 구조: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")

            # 첫 페이지에서 totalCount 확인
            if page == 1:
                total_count = data.get('totalCount', 0)
                if total_count == 0:
                    print(f"ℹ 단지 {complex_no}의 매물이 없습니다.")
                    print("응답 데이터 키:", list(data.keys()))
                    break
                total_pages = min((total_count + 19) // 20, max_pages)  # 20개씩 표시, max_pages 제한
                print(f" 단지 {complex_no}의 총 {total_count}개 매물 발견 (총 {total_pages}페이지)")

                # 첫 페이지의 메타데이터 복사
                combined_result["isMoreData"] = data.get("isMoreData", False)
                combined_result["mapExposedCount"] = data.get("mapExposedCount", 0)
                combined_result["nonMapExposedIncluded"] = data.get("nonMapExposedIncluded", False)

            articles = data.get("articleList", [])
            if not articles:
                print(f" 단지 {complex_no}의 {page}페이지에 더 이상 매물 없음.")
                print("응답 데이터 키:", list(data.keys()))
                break

            combined_result["articleList"].extend(articles)
            print(f" 단지 {complex_no}의 {page}/{total_pages}페이지에서 {len(articles)}건 수집됨.")
            
            # 더 이상 데이터 없음 플래그가 false면 중단
            if not data.get("isMoreData", False):
                break

            page += 1
            time.sleep(0.3)  # API 호출 간 딜레이 (300ms)

        except Exception as e:
            print(f" 단지 {complex_no}의 {page}페이지 오류 발생: {str(e)}")
            if hasattr(e, 'response'):
                print(f"응답 상태 코드: {e.response.status_code}")
                print(f"응답 내용: {e.response.text[:500]}...")
            break

    return combined_result

def flatten_articles(all_data):
    """모든 단지의 매물을 하나의 리스트로 평탄화"""
    all_articles = []
    for complex_no, data in all_data.items():
        for article in data['articleList']:
            article['complexNo'] = complex_no  # 단지 번호 추가
            all_articles.append(article)
    return all_articles

def main():
    # 지역 설정
    city = '서울특별시'
    district = '마포구'
    
    # 단지 목록 가져오기
    print(f"\n {city} {district} 단지 목록 가져오는 중...")
    complex_numbers = get_complex_list_by_dong(city, district)
    
    if not complex_numbers:
        print(" 단지 목록을 가져오지 못했습니다. 프로그램을 종료합니다.")
        return
    
    # 각 단지별로 크롤링
    all_data = {}
    total_articles = 0

    for complex_no in complex_numbers:
        print(f"\n단지 {complex_no} 크롤링 시작...")
        result = crawl_complex(complex_no)
        all_data[str(complex_no)] = result
        article_count = len(result['articleList'])
        total_articles += article_count
        print(f" 단지 {complex_no} 완료: {article_count}건 수집")
        time.sleep(2)

    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 원본 구조 저장
    structured_filename = f'naver_land_structured_{city}_{district}_{timestamp}.json'
    with open(structured_filename, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n 구조화된 데이터 저장 완료: {structured_filename}")
    
    # 평탄화된 데이터 저장
    flattened_articles = flatten_articles(all_data)
    flattened_filename = f'naver_land_flattened_{city}_{district}_{timestamp}.json'
    with open(flattened_filename, 'w', encoding='utf-8') as f:
        json.dump(flattened_articles, f, ensure_ascii=False, indent=2)
    print(f" 평탄화된 데이터 저장 완료: {flattened_filename}")
    print(f" 총 {len(complex_numbers)}개 단지, {total_articles}개 매물 수집 완료!")

if __name__ == "__main__":
    main()
