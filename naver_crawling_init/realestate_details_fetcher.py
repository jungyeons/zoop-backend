import requests
import json
import time
import random
from datetime import datetime, timedelta
import os
import glob

#  최신 인증 정보
HEADERS = {
    "user-agent": "비공개",
    "authorization": "비공개",
    "referer": "비공개",
    # "...이하 비공개
}

COOKIES = {
    "NNB": "비공개",
    "NaverSuggestUse": "비공개"
    # "...이하 비공개

}

def get_complex_info(complex_no, session, max_retries=3):
    """
    단지 정보를 가져오는 함수
    
    Args:
        complex_no (str): 단지 번호
        session (requests.Session): 세션 객체
        max_retries (int): 최대 재시도 횟수
    
    Returns:
        dict: 단지 정보 (성공 시)
        None: 실패 시
    """
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            complex_info_url = f'https://new.land.naver.com/api/complexes/{complex_no}'
            print(f" 단지 정보 요청: {complex_info_url}")
            
            complex_headers = HEADERS.copy()
            complex_headers['referer'] = f'https://new.land.naver.com/complexes/{complex_no}'
            complex_headers['accept'] = '*/*'
            
            complex_response = session.get(complex_info_url, headers=complex_headers, cookies=COOKIES)
            if complex_response.status_code == 200:
                return complex_response.json()
            else:
                print(f" 단지 정보 요청 실패: {complex_response.status_code}")
                retry_count += 1
                time.sleep(2)
                
        except Exception as e:
            print(f" 오류 발생: {str(e)}")
            retry_count += 1
            time.sleep(2)
    
    return None

def get_article_details(article_no, session, max_retries=3):
    """
    매물 상세 정보를 가져오는 함수
    
    Args:
        article_no (str): 매물 번호
        session (requests.Session): 세션 객체
        max_retries (int): 최대 재시도 횟수
    
    Returns:
        dict: 매물 상세 정보 (성공 시)
        None: 실패 시
    """
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            article_url = f'https://new.land.naver.com/api/articles/{article_no}?complexNo='
            print(f" 매물 상세 정보 요청: {article_url}")
            
            article_headers = HEADERS.copy()
            article_headers['referer'] = f'https://new.land.naver.com/complexes?ms=0,0,0&a=APT:ABYG:JGC:PRE&b=A1:B1:B2&e=RETAIL&f=5000&articleNo={article_no}'
            
            response = session.get(article_url, headers=article_headers, cookies=COOKIES)
            if response.status_code == 200:
                return response.json()
            else:
                print(f" 매물 상세 정보 요청 실패: {response.status_code}")
                retry_count += 1
                time.sleep(2)
                
        except Exception as e:
            print(f" 오류 발생: {str(e)}")
            retry_count += 1
            time.sleep(2)
    
    return None

def get_articles_by_complex(complex_no, max_retries=3):
    """
    단지의 매물 정보를 가져오는 함수
    
    Args:
        complex_no (str): 단지 번호
        max_retries (int): 최대 재시도 횟수
    
    Returns:
        dict: 매물 정보 (성공 시)
        None: 실패 시
    """
    session = requests.Session()
    retry_count = 0
    all_articles = []
    page = 1
    
    while retry_count < max_retries:
        try:
            # 1. 메인 페이지 접근 (세션 초기화)
            main_url = 'https://new.land.naver.com/'
            print(f" 메인 페이지 접근: {main_url}")
            
            main_headers = HEADERS.copy()
            main_headers['sec-fetch-mode'] = 'navigate'
            main_headers['sec-fetch-dest'] = 'document'
            main_headers['sec-fetch-user'] = '?1'
            
            main_response = session.get(main_url, headers=main_headers, cookies=COOKIES)
            if main_response.status_code != 200:
                print(f" 메인 페이지 접근 실패: {main_response.status_code}")
                retry_count += 1
                time.sleep(0.2)
                continue
            
            # 2. 단지 페이지 접근
            complex_page_url = f'https://new.land.naver.com/complexes/{complex_no}'
            print(f" 단지 페이지 접근: {complex_page_url}")
            
            page_headers = HEADERS.copy()
            page_headers['referer'] = main_url
            page_headers['sec-fetch-mode'] = 'navigate'
            page_headers['sec-fetch-dest'] = 'document'
            page_headers['sec-fetch-user'] = '?1'
            
            page_response = session.get(complex_page_url, headers=page_headers, cookies=COOKIES)
            if page_response.status_code != 200:
                print(f" 단지 페이지 접근 실패: {page_response.status_code}")
                retry_count += 1
                time.sleep(0.2)
                continue
            
            # 3. 단지 정보 가져오기
            complex_info = get_complex_info(complex_no, session)
            if not complex_info:
                print(" 단지 정보를 가져오지 못했습니다.")
                retry_count += 1
                time.sleep(0.2)
                continue
            
            # 4. 매물 목록 API 호출 (모든 페이지)
            while True:
                articles_url = f'https://new.land.naver.com/api/articles/complex/{complex_no}?realEstateType=APT&tradeType=A1&page={page}&type=list&order=rank'
                print(f" 매물 정보 요청 (페이지 {page}): {articles_url}")
                
                # 매물 API 요청 시 필요한 헤더 설정
                dynamic_headers = HEADERS.copy()
                dynamic_headers['referer'] = f'https://new.land.naver.com/complexes/{complex_no}?ms=37.5575,126.9083,16&a=APT:ABYG:JGC:PRE&b=A1&e=RETAIL&g=114400&f=114400'
                dynamic_headers['sec-fetch-site'] = 'same-origin'
                dynamic_headers['sec-fetch-mode'] = 'cors'
                dynamic_headers['sec-fetch-dest'] = 'empty'
                
                # 랜덤 딜레이 (0.03~0.05초)
                random_sec = random.uniform(0.03, 0.05)
                print(f" {random_sec:.2f}초 대기 중...")
                time.sleep(random_sec)
                
                # API 요청
                response = session.get(articles_url, headers=dynamic_headers, cookies=COOKIES)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articleList', [])
                    
                    if not articles:  # 더 이상 매물이 없으면 종료
                        break
                    
                    # 각 매물의 상세 정보 가져오기
                    for article in articles:
                        article_no = article.get('articleNo')
                        if article_no:
                            article_details = get_article_details(article_no, session)
                            if article_details:
                                # 기존 매물 정보에 상세 정보 추가
                                article.update({
                                    'articleDetails': article_details
                                })
                    
                    all_articles.extend(articles)
                    print(f" 페이지 {page} 매물 정보 수집 성공: {len(articles)}개 매물")
                    
                    # 다음 페이지로
                    page += 1
                    
                    # 페이지 간 딜레이 (0.02~0.04초)
                    time.sleep(random.uniform(0.02, 0.04))
                    
                elif response.status_code == 401:
                    print(" 인증 실패: 세션이 만료되었거나 유효하지 않습니다.")
                    print(" 해결방법: 브라우저에서 네이버 부동산에 로그인하고 F12 > 네트워크에서 다음 정보를 복사해주세요:")
                    print("1. NID_AUT 쿠키 값")
                    print("2. Authorization 헤더 값")
                    retry_count += 1
                    break
                elif response.status_code == 403:
                    print(" 접근 거부: Referer 헤더가 유효하지 않습니다.")
                    print(" 해결방법: 브라우저에서 네이버 부동산에 로그인하고 F12 > 네트워크에서 정확한 Referer를 복사해주세요.")
                    retry_count += 1
                    break
                else:
                    print(f" 매물 요청 실패 - {complex_no}, 상태코드: {response.status_code}")
                    if hasattr(response, 'text'):
                        print(f"응답 내용: {response.text[:500]}...")
                    retry_count += 1
                    break
            
            if all_articles:
                # 단지 정보와 매물 정보를 합침
                result = {
                    'complexInfo': complex_info,
                    'articleList': all_articles,
                    'totalArticles': len(all_articles)
                }
                print(f" 총 {len(all_articles)}개의 매물 정보 수집 완료")
                return result
            
            retry_count += 1
            time.sleep(0.2)
            
        except Exception as e:
            print(f" 오류 발생: {str(e)}")
            retry_count += 1
            time.sleep(0.2)
    
    print(f" 최대 재시도 횟수({max_retries})를 초과했습니다.")
    return None

def process_complex_list(json_file):
    """
    단지 목록 JSON 파일을 처리하는 함수
    
    Args:
        json_file (str): JSON 파일 경로
    """
    try:
        # JSON 파일 읽기
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 결과를 저장할 데이터 구조
        result_data = {
            'city': data['city'],
            'district': data['district'],
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'total_complexes': data['total_complexes'],
            'complexes': []
        }
        
        # 전체 단지 수 계산
        total_complexes = sum(len(complexes) for complexes in data['dong_complexes'].values())
        processed_complexes = 0
        
        # 시작 시간 기록
        start_time = datetime.now()
        
        # 각 동별로 처리
        for dong, complexes in data['dong_complexes'].items():
            print(f"\n {dong} 처리 중...")
            
            # 동별 결과를 저장할 데이터 구조
            dong_data = {
                'city': data['city'],
                'district': data['district'],
                'dong': dong,
                'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
                'total_complexes': len(complexes),
                'complexes': []
            }
            
            for complex_info in complexes:
                complex_no = complex_info['complexNo']
                complex_name = complex_info['complexName']
                
                # 진행률 계산
                processed_complexes += 1
                progress_percentage = (processed_complexes / total_complexes) * 100
                
                # 예상 완료 시간 계산
                elapsed_time = (datetime.now() - start_time).total_seconds()
                if processed_complexes > 1:  # 첫 번째 단지 이후부터 계산
                    avg_time_per_complex = elapsed_time / (processed_complexes - 1)
                    remaining_complexes = total_complexes - processed_complexes
                    estimated_remaining_seconds = avg_time_per_complex * remaining_complexes
                    estimated_completion_time = datetime.now() + timedelta(seconds=estimated_remaining_seconds)
                    time_str = estimated_completion_time.strftime("%H:%M:%S")
                else:
                    time_str = "계산 중..."
                
                # 이미 처리된 단지인지 확인
                if any(c['complexInfo']['complexNo'] == complex_no for c in dong_data['complexes']):
                    print(f" {complex_name}({complex_no})는 이미 처리되었습니다. 건너뜁니다. (전체 진행률: {progress_percentage:.1f}%, 예상 완료: {time_str})")
                    continue
                
                print(f"\n {complex_name}({complex_no}) 처리 중... (전체 진행률: {progress_percentage:.1f}%, 예상 완료: {time_str})")
                
                try:
                    # 매물 정보 가져오기
                    result = get_articles_by_complex(complex_no)
                    
                    if result:
                        # 단지 정보와 매물 정보를 합침
                        complex_data = {
                            'complexInfo': complex_info,
                            'articles': result['articleList'],
                            'totalArticles': result['totalArticles']
                        }
                        dong_data['complexes'].append(complex_data)
                        result_data['complexes'].append({
                            'dong': dong,
                            **complex_data
                        })
                        print(f" {complex_name}의 {result['totalArticles']}개 매물 정보 수집 완료 (전체 진행률: {progress_percentage:.1f}%, 예상 완료: {time_str})")
                        
                        # 랜덤 딜레이 (0.17~0.33초)
                        random_sec = random.uniform(0.17, 0.33)
                        print(f" {random_sec:.2f}초 대기 중...")
                        time.sleep(random_sec)
                    else:
                        print(f" {complex_name}({complex_no})의 매물 정보를 가져오지 못했습니다. (전체 진행률: {progress_percentage:.1f}%, 예상 완료: {time_str})")
                        
                except Exception as e:
                    print(f" {complex_name}({complex_no}) 처리 중 오류 발생: {str(e)} (전체 진행률: {progress_percentage:.1f}%, 예상 완료: {time_str})")
                    continue
            
            # 동별 결과 저장
            dong_filename = f'complex_details_{data["district"]}_{dong}_{dong_data["timestamp"]}.json'
            with open(dong_filename, 'w', encoding='utf-8') as f:
                json.dump(dong_data, f, ensure_ascii=False, indent=2)
            print(f"\n {dong}의 단지 정보가 {dong_filename}에 저장되었습니다. (전체 진행률: {progress_percentage:.1f}%, 예상 완료: {time_str})")
            
            # 동 처리 후 잠시 대기 (0.33~0.5초)
            if dong != list(data['dong_complexes'].keys())[-1]:  # 마지막 동이 아닌 경우에만 대기
                random_sec = random.uniform(0.33, 0.5)
                print(f" 다음 동 처리 전 {random_sec:.2f}초 대기 중...")
                time.sleep(random_sec)
        
        # 전체 결과 저장
        output_filename = f'complex_details_{data["district"]}_all_{result_data["timestamp"]}.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # 실제 소요 시간 계산
        total_time = (datetime.now() - start_time).total_seconds()
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)
        
        print(f"\n 모든 단지 정보가 {output_filename}에 저장되었습니다.")
        print(f"\n⏱ 총 소요 시간: {hours}시간 {minutes}분 {seconds}초")
        
        # 통계 출력
        total_articles = sum(complex['totalArticles'] for complex in result_data['complexes'])
        print(f"\n 수집 통계:")
        print(f"- 총 단지 수: {len(result_data['complexes'])}개")
        print(f"- 총 매물 수: {total_articles}개")
        
    except Exception as e:
        print(f" 오류 발생: {str(e)}")
        if 'result_data' in locals() and result_data['complexes']:
            # 오류 발생 시 현재까지의 진행 상황 저장
            error_filename = f'complex_details_{data["district"]}_error_{result_data["timestamp"]}.json'
            with open(error_filename, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            print(f" 오류 발생으로 인해 현재까지의 진행 상황이 {error_filename}에 저장되었습니다.")

def main():
    # JSON 파일 경로
    json_file = 'complex_list_서울특별시_마포구_*.json'  # 마포구 JSON 파일 패턴
    
    # 가장 최근 파일 찾기
    files = glob.glob(json_file)
    if not files:
        print(" 마포구 단지 목록 파일을 찾을 수 없습니다.")
        return
    
    latest_file = max(files, key=os.path.getctime)
    print(f" 처리할 파일: {latest_file}")
    
    # 단지 목록 처리
    process_complex_list(latest_file)
    
    print("\n 모든 단지 정보 수집이 완료되었습니다.")

if __name__ == "__main__":
    main()
