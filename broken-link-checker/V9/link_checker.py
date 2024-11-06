from pprint import pprint
import os, re, sys
sys.path.append('C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/')
import common.ray_tools as ray_tools
import asyncio
import socket
import aiohttp
from typing import List
from typing import TextIO

lock = asyncio.Lock()

class URL:
    def __init__(self, url: str):
        self.url = url
        self.result = None
        self.is_abs = None
        self.is_rel = None
        self.local_rel_url = None
        self.changed_url = None

    def __str__(self):
        return self.url

    def __repr__(self):
        return self.url

    def __eq__(self, other):
        if isinstance(other, URL):
            return self.url == other.url
        elif isinstance(other, str):
            return self.url == other
        else:
            return False

    def __hash__(self):
        return hash(self.url)
    
    def set_result(self, result: bool, reason: str = None):
        if self.result != None:
            raise RuntimeError("링크 작동 결과값을 덮어쓸 수 없습니다.")
        else:
            self.reason = reason
            self.result = result
            
    def get_result(self):
        return self.result
        
    def set_changed_url(self, url: str):
        self.changed_url = url
        
    def set_local_rel_url(self, url: str):
        if self.is_rel == True:
            self.local_rel_url = url
        elif self.is_rel == False:
            raise RuntimeError("상대경로가 아닙니다.")
        else:
            raise RuntimeError("절대/상대 여부를 먼저 설정해주세요.")
        
    def set_abs(self):
        if self.is_abs != None:
            raise RuntimeError("절대/상대 여부를 덮어쓸 수 없습니다.")
        self.is_abs = True
        self.is_rel = False
    
    def set_rel(self):
        if self.is_rel != None:
            raise RuntimeError("절대/상대 여부를 덮어쓸 수 없습니다.")
        self.is_rel = True
        self.is_abs = False
    
    
CV_DICT_KO = {"[cgv hive_sdk4_unity_api_ref]":"https://developers.withhive.com/HTML/v4_api_reference/Unity3D",
    "[cgv hive_sdk4_android_api_ref]":"https://developers.withhive.com/HTML/v4_api_reference/Android",
    "[cgv hive_sdk4_ios_api_ref]":"https://developers.withhive.com/HTML/v4_api_reference/iOS",
    "[cgv hive_sdk4_cpp_api_ref]":"https://developers.withhive.com/HTML/v4_api_reference/CPP",
}

CV_DICT_EN = {"[cgv hive_sdk4_unity_api_ref_en]":"https://developers.withhive.com/HTML/v4_api_reference_en/Unity3D",
    "[cgv hive_sdk4_android_api_ref_en]":"https://developers.withhive.com/HTML/v4_api_reference_en/Android",
    "[cgv hive_sdk4_ios_api_ref_en]":"https://developers.withhive.com/HTML/v4_api_reference_en/iOS",
    "[cgv hive_sdk4_cpp_api_ref_en]":"https://developers.withhive.com/HTML/v4_api_reference_en/CPP",
}

LANGUAGE = 'ko'

semaphore = asyncio.Semaphore(10)

def custom_variable_parser(url : str, replacements : dict):
    for target, replacement in replacements.items():
        if target in url:
            url = url.replace(target, replacement)
    return url

def wordpress_to_local_format(rel_url):
    # 워드프레스에서 쓰는 상대경로 (상위 path로 1단계 올림)를 원래 상대경로로 바꿔줌
    # 1단계씩 "제거"함.
    if rel_url.startswith("../../"):
        return rel_url.replace("../../", "../")
    elif rel_url.startswith("../"):
        return rel_url.replace("../", "./")
    else:
        return rel_url

async def check_rel_url(file_path, rel_url: URL):
    _id = None
    
    # # 태그가 있는 경우
    if '#' in rel_url.local_rel_url:
        _parsed = rel_url.local_rel_url.split('#')
        # 동일 페이지 내 앵커로 이동하는 경우
        # 예시: "#idp-check"
        # 다른 페이지 내 앵커로 이동하는 경우
        # 예시: "../../idp-connect-helper#idp-check"
        if _parsed[1] != '':
            parsed_local_rel_url, _id = _parsed[0], _parsed[1]
        # 잘못된 형식
        # 예시: "idp-connect-helper#"
        else:
            rel_url.set_result(False, '#는 있는데 id 값이 없습니다.')
            return        
    # # 태그가 없는 경우
    else:
        parsed_local_rel_url = rel_url.local_rel_url
       
    # rel_url에 id만 존재하는 경우 full_path 수정
    if _id and parsed_local_rel_url == '':
        full_path = file_path
        
    # rel_url 잘못 설정한 경우 미리 걸러냄
    # rel_url이 마크다운 파일이 아닌 경우 (그냥 디렉토리거나 잘못된 문자인 경우)
    elif not parsed_local_rel_url.endswith('.md'):
        rel_url.set_result(False, '상대경로가 마크다운 페이지가 아닙니다. 그냥 디렉토리 이거나 잘못된 경로일 수 있습니다.')
        return
    # 그 외의 경우
    else:
        # Get the directory of the current file
        current_dir = os.path.dirname(file_path)

        # Combine the directory with the relative link and normalize the path
        full_path = os.path.normpath(os.path.join(current_dir, parsed_local_rel_url))

    # Check if the file exists
    if os.path.exists(full_path):
        # id가 있으면 id도 체크
        if _id:
            async with lock:
                # read full_path and check if id exists using BeautifulSoup
                with open(full_path, 'r', encoding='utf-8') as md_file:
                    md = md_file.read()
                    id_target = "{ #" + f"{_id}" + " }"
                    # id가 있으면 id_found는 0 또는 양수, 없으면 -1
                    id_found = md.find(id_target)
                    
                    if id_found >= 0:
                        rel_url.set_result(True)
                        return
                    else:
                        rel_url.set_result(False, "상대경로를 따라 다른 페이지로 이동했는데, 페이지에 해당 id가 없습니다.")
                        return
        # id가 없을 때, full_path만 존재하면 True 
        else:
            rel_url.set_result(True)
            return
    else:
        rel_url.set_result(False, "이동할 페이지가 존재하지 않습니다.")
        return

def get_all_md_file_paths(dir):
    md_file_paths = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith('.md'):
                md_file_paths.append(os.path.join(root, file))
    return md_file_paths

def check_lang(abs_url: URL):
    if abs_url.changed_url:
        abs_url_str = abs_url.changed_url
    else:
        abs_url_str = abs_url.url
    
    # Hive 개발자 사이트인 경우만 체크 
    if abs_url_str.startswith('https://developers.withhive.com/'):
        # 영문 Unity, C++, Android, iOS API doc
        if abs_url_str.startswith('https://developers.withhive.com/HTML/v4_api_reference_en/'):
            api_doc = True
            en_doc = True
            ko_doc = False
        # 국문 Unity, C++, Android, iOS API doc
        elif abs_url_str.startswith('https://developers.withhive.com/HTML/v4_api_reference/'):
            api_doc = True
            ko_doc = True
            en_doc = False
        # Swfit API doc
        elif abs_url_str.startswith('https://developers.withhive.com/documentation/'):
            api_doc = True
            ko_doc = False
            en_doc = False
        # Kotlin API doc
        elif abs_url_str.startswith('https://developers.withhive.com/HTML/dokka/'):
            api_doc = True
            ko_doc = False
            en_doc = False
        else:
            api_doc = False
        
        if api_doc:
            # Unity, C++, Android, iOS API 국문 문서 다국어 경로 체크
            if LANGUAGE == 'ko' and en_doc:
                abs_url.set_result(False, '한국어 페이지가 아닙니다.')
                return
            # Unity, C++, Android, iOS API 영문 문서 다국어 경로 체크
            elif LANGUAGE == 'en' and ko_doc:
                abs_url.set_result(False, '영문 페이지가 아닙니다.')
                return
            # Kotlin/Swift는 다국어 경로 체크 필요 없음
            else:
                return
        else:
            if LANGUAGE == 'ko' and '/ko/' not in abs_url_str:
                abs_url.set_result(False, '한국어 페이지가 아닙니다.')
                return
            # 영문 페이지가 아닌데 영문으로 접근하는 경우. 영문 페이지는 언어 분기값이 경로에 없음.
            elif LANGUAGE == 'ko' and '/ko/' not in abs_url_str and '/en/' not in abs_url_str:
                abs_url.set_result(False, '한국어 페이지가 아닙니다.')
                return
            elif LANGUAGE == 'en' and '/ko/' in abs_url_str:
                abs_url.set_result(False, '영문 페이지가 아닙니다.')
                return
            else:
                return
    else:
        return
    
        
async def _check_connection(session, abs_url : URL):
    if abs_url.changed_url:
        abs_url_str = abs_url.changed_url
    else:
        abs_url_str = abs_url.url
        
    try:
        async with session.get(abs_url_str, allow_redirects=True, timeout=15) as response:
            abs_url.set_result(response.status == 200, f'HTTP 상태 코드: {response.status}')
    except aiohttp.ClientConnectorError as e:
        if isinstance(e.__cause__, socket.gaierror):
            abs_url.set_result(False, 'DNS 오류: 주소를 찾을 수 없습니다.')
        else:
            abs_url.set_result(False, f'연결할 수 없는 주소입니다: {str(e)}')
    except aiohttp.ClientConnectorError:
        abs_url.set_result(False, '연결할 수 없는 주소입니다.')
    except aiohttp.ClientError:
        abs_url.set_result(False, '연결할 수 없는 주소입니다.')
    except asyncio.TimeoutError:
        abs_url.set_result(False, '연결 시간이 초과되었습니다.')
    except Exception as e:
        print(e)
        abs_url.set_result(False, '알 수 없는 오류가 발생했습니다.')
    return

@ray_tools.do_on_single_file
def extract_links(content:str) -> tuple[list, list]:
    abs_urls = []
    rel_urls = []
    
    # Removing code blocks from the extraction range
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r'<pre>.*?<\/pre>', '', content, flags=re.DOTALL)
    
    links = re.findall(r'\[.*?\]\((.*?)\)', content)
    
    for link in links:
        url = URL(link)
        
        # Skipping image files
        # img: \[!\[\]\((.*?)\)
        if url.url.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            continue
        
        # 절대경로, 상대경로 구분
        
        # 빈 값이면 일단 절대 경로로 처리 (절대 경로는 사전에 False 걸러내는 처리를 나중에 하기 때문)
        if url.url == '':
            url.set_result(False, '링크가 빈 값입니다.')
            abs_urls.append(url)
        # 커스톰 변수로 시작하는 API 문서: 일반 절대 경로로 바꾼 후 처리
        elif url.url.startswith('[cgv'):
            url.set_abs()
            if LANGUAGE == 'ko':
                url.set_changed_url(custom_variable_parser(url.url, CV_DICT_KO))
            elif LANGUAGE == 'en':
                url.set_changed_url(custom_variable_parser(url.url, CV_DICT_EN))
            else:
                raise RuntimeError("LANGUAGE 설정값이 올바르지 않습니다.")
            check_lang(url)
            abs_urls.append(url)
        elif url.url.startswith('http'):
            url.set_abs()
            check_lang(url)
            abs_urls.append(url)
        else:
            url.set_rel()
            # url.set_local_rel_url(wordpress_to_local_format(url.url))
            url.set_local_rel_url(url.url)
            rel_urls.append(url)
    return abs_urls, rel_urls
                    
async def check_connections(abs_urls : list):
    # handle abs_links
    async with semaphore, aiohttp.ClientSession() as session:
        abs_tasks = []
        for abs_url in abs_urls:
            abs_task = asyncio.create_task(_check_connection(session, abs_url))
            abs_tasks.append(abs_task)
        await asyncio.gather(*abs_tasks)

async def find_and_check_rel_links(file_path, rel_urls: List[URL]):
    # handle rel_links
    rel_tasks = []
    for rel_url in rel_urls:
        rel_task = asyncio.create_task(check_rel_url(file_path, rel_url))
        rel_tasks.append(rel_task)
    await asyncio.gather(*rel_tasks)

@ray_tools.async_do_on_multiple_files
async def check_files(file_path):
    abs_urls, rel_urls = extract_links(file_path)
    
    # 결과가 False로 된 abs_url은 제외
    abs_urls_next = [url for url in abs_urls if url.get_result() == None]
    
    # 사이트 접속 체크
    await asyncio.gather(*(check_connections(abs_urls_next),
                            find_and_check_rel_links(file_path, rel_urls)))
    # 결과 저장
    # 결과가 아직도 None인 경우면 에러 발생
    assert all(abs_url.get_result() != None for abs_url in abs_urls)
    assert all(rel_url.get_result() != None for rel_url in rel_urls)
    
    file_results = {}
    for abs_url in abs_urls:
        file_results[abs_url.url] = abs_url
    for rel_url in rel_urls:
        file_results[rel_url.url] = rel_url
    return file_results

@ray_tools.do_create_report
def create_report(result_file: TextIO, result: dict[str, URL]):
    for url_str, url in result.items():
        if url.result == False:
            result_file.write(f"{url_str}  {url.reason}\n")
    result_file.write('\n\n')
    
def check(root_paths):
    for i, root_path in enumerate(root_paths):
        result = asyncio.run(check_files(root_path))
        result_path = os.path.dirname(__file__) + f'\\output_{i}'
        create_report(root_path, result_path, result)
            
def main():
    root_paths = [
        'C:/Users/khy/Documents/workspace/devsite_mk/docs/en/dev'
    ]

    check(root_paths)
    
if __name__ == "__main__":
    main()

'''
TODO:
5. UI 구현
'''