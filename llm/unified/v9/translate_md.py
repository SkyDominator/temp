import os, sys, time, json, requests
sys.path.append("C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/common/")
import ray_tools_git, ray_tools
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import re
import copy

load_dotenv(r'C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/llm/env/data.env')
GPT4_O_MINI_APP_KEY = os.getenv('GPT4-O-MINI-APP-KEY')
GPT4_O_MINI_APP_SIGNATURE = os.getenv('GPT4-O-MINI-APP-SIGNATURE')

POST_URL = "https://ats.withhive.com/api/translate/async"
HEADERS = {
    "Content-Type": "application/json",
    "Signature": GPT4_O_MINI_APP_SIGNATURE
}

def load_system_prompt(from_lang) -> str:
    # 프롬프트
    prompt = f"You are a professional translator in IT field. There are a few rules you must follow in the translation: Do not modify the links in the source document."
    
    if from_lang == 'en':
        prompt += " Apply Sentence Case to section titles during translation."
    
    prompt += f" In the translation results, preserve the English string starting with '__EXCEPT_CONTENTS_OBJECT_' as it is. Maintain languages other than source and target language as they are. Return only the translated contents."
    
    # do some other tasks
    
    final_sentence = " Here comes the source language texts to translate:"
    prompt += final_sentence
    return prompt
  
BASE_PATH = os.path.normpath(r"C:\Users\raykim\Documents\workspace\devsite_mk")

NO_TRANSLATION = {
    "white-labeling-1": r'%% brand_name %%', 
    "white-labeling-2": r'%% project_name %%',
    # "code-block": r'```.*?```',
    # "markdown-table": r'(?:(?:^\s*\|.+\|[ \t]*$\n?)+(?:^\s*\|[-:| ]+\|[ \t]*$\n?)?(?:^\s*\|.+\|[ \t]*$\n?)+)',
    # "html-table": r'<table.*?/table>',
}

TARGET_LANGS = ['ja', 'ko', 'th', 'zh', 'zh-Hant']  # List of target languages

# 영역이 구분자로 구분되어 분명한 패턴들
FIRST_PATTERNS = [
    # primary
    {'name': 'code_block', 'pattern': r'```.*?```'},
    {'name': 'html_table', 'pattern': r'<table.*?>.*?<\/table>'},
    {'name': 'html_u_list', 'pattern': r'<ul.*?>.*?<\/ul>'},
    {'name': 'html_o_list', 'pattern': r'<ol.*?>.*?<\/ol>'},
    {'name': 'code_tabs', 'pattern': r'=== (?:\"|\').+?(?:\"|\')'},
    {'name': 'heading', 'pattern': r'^(?:#{1,6}) .*?$'},
    {'name': 'html_heading', 'pattern': r'<h[1-6].*?>.*?<\/h[1-6]>'},
    {'name': 'horizontal_rule', 'pattern': r'^-{3,}$'},
    {'name': 'horizontal_rule_html', 'pattern': r'<hr.*?>'},
]

PATTERNS_2 = [
    # noteblock
    {'name': 'note_block', 'pattern': r'\?\?\?\+ \S+\n.*?\n\n(?!(?:\t|\s{2,4})\S)'},
    # md table
    {'name': 'markdown-table', 'pattern': r'(?:(?:^\s*\|.+\|[ \t]*$\n?)+(?:^\s*\|[-:| ]+\|[ \t]*$\n?)?(?:^\s*\|.+\|[ \t]*$\n?)+)'},
]

PATTERNS_3 = [
    # md list
    {'name': 'list', 'pattern': r'^(?:\s*(?:\*|\-|\d+\.|\+)) .*?\n\n(?!\s*(?:\* |\- |\d+\. |\+ ))'},
    {'name': 'paragraph', 'pattern': r'\S.*?(?=\n|\Z)'},
]

def translate_text(text:str, from_lang:str, to_lang_list: List[str], **kwargs) -> dict[str, str]:
    if kwargs.get('prompt', False) and kwargs['prompt'] == True:
        prompt = load_system_prompt(from_lang)
        text = f"{prompt}\n\n{text}"
    
    to_lang = ",".join(to_lang_list)
    payload = {
        "info": {
            "app_key": GPT4_O_MINI_APP_KEY
        },
        "text": f"{text}",
        "to": f"{to_lang}",
        "from": f"{from_lang}"
    }
    response = requests.post(POST_URL, headers=HEADERS, data=json.dumps(payload))
    response_result = response.json()
    
    if response.status_code == 200:
        print(f"Request for translation was successful: {response.status_code}")
    else:
        raise ValueError(f"Request Status Code: {response.status_code}")
    
    if response_result['result']['code'] != 200:
        raise ValueError(f"Request Result Code: {response_result['result']['code']}, {response_result['result']['msg']}")
    
    get_url = f"https://ats.withhive.com/api/translate/async/result/{response_result['content']['uuid']}"

    while True:
        response = requests.get(get_url, headers=HEADERS)
        response_result = response.json()

        if response_result['result']['code'] != 200:
            raise ValueError(f"Error: {response_result['result']['code']}, {response_result['result']['message']}")
        
        if response_result['content']['status']['code'] == 100 and response_result['content']['status']['msg'] == "completed":
            translations_list = response_result['content']['data']['translateMsg']
            break
        else:
            print(f"Status: {response_result['content']['status']['code']}, {response_result['content']['status']['msg']}")
            time.sleep(1)
            continue
    
    result = {}
    for translation in translations_list:
        for translated_text in translation['translations']:
            result[translated_text['to']] = translated_text['text']
    return result


def load_system_prompt(from_lang:str, to_lang: str) -> str:
    LANGS = {'en': 'English', 'ja': 'Japanese', 'ko': 'Korean', 'th': 'Thai', 'zh': 'Simplified Chinese', 'zh-Hant': 'Traditional Chinese'}
    from_lang = from_lang.lower()
    to_lang = to_lang.lower()
    source = LANGS[from_lang]
    target = LANGS[to_lang]
    
    # 프롬프트
    prompt = f"You are a professional {source}-{target} translator in IT field. Translate all the content I provide into {target}. There are a few rules you must follow in the translation: Do not modify the links in the {source} document. Translate {source} comments into {target} in the code blocks."
    
    if from_lang == 'en':
        prompt += " Apply Sentence Case to section titles during translation."
    
    prompt += f" Preserve the English string starting with '__EXCEPT_CONTENTS_OBJECT_' as it is in the translation results. Maintain languages other than {source} and {target} as is. Return only the translated contents."
    
    return {to_lang : prompt}
 
def parse_markdown(markdown_content: str) -> list:
    parsed_elements = []
    remaining_content = markdown_content
    
    def update(content, start, end, name=None):
        if name is None:
            name=pattern['name']
        parsed_elements.append({
            "type": name,
            "content": content,
            "start": start,
            "end": end
        })
    
    def find_non_overlapping_matches(pattern: str, text: str) -> List[Dict[str, any]]:
        matches = []
        start = 0
        while start < len(text):
            pos = text.find(pattern, start)
            if pos == -1:
                break
            match_content = text[pos:pos + len(pattern)]
            matches.append({
                "start": pos,
                "end": pos + len(pattern),
                "content": match_content
            })
            start = pos + len(pattern)
        return matches

    
    def update_first_pattners(patterns):
        nonlocal remaining_content
        for pattern in patterns:
            # if pattern['name'] == 'list':
            #     print('hold')
            if pattern['name'] in ['heading', 'horizontal_rule', 'markdown-table', 'list']:
                match_objects = re.finditer(pattern['pattern'], markdown_content, re.MULTILINE | re.DOTALL)
            else:
                match_objects = re.finditer(pattern['pattern'], markdown_content, re.DOTALL)
                
            matches = [match for i, match in enumerate(match_objects)]
            if len(matches) > 0:
                for match in matches:
                    content = match.group(0)
                    update(content, match.start(), match.end(), name=pattern['name'])
                    remaining_content = remaining_content.replace(content, "", 1)
            else:
                continue
        
    def update_patterns(patterns):
        nonlocal remaining_content
        for pattern in patterns:
            if pattern['name'] in ['heading', 'horizontal_rule', 'markdown-table']:
                match_objects = re.finditer(pattern['pattern'], remaining_content, re.MULTILINE | re.DOTALL)
            else:
                match_objects = re.finditer(pattern['pattern'], remaining_content, re.DOTALL)
            for match in match_objects:
                content = match.group(0)
                if content.strip() == '<br>' or content.strip() == '<br/>' or content.strip() == '<br />':
                    continue
                content = content.strip()
                second_match_objects = find_non_overlapping_matches(content, markdown_content)
                for second_match in second_match_objects:    
                    second_content = second_match['content']
                    update(second_content, second_match['start'], second_match['end'], name=pattern['name'])
                    remaining_content = remaining_content.replace(second_content, "", 1)
    
    # paragraph 패턴을 제외한 다른 패턴들을 탐색

    
    # 불 분명한 패턴들 탐색
    # paragraph_pattern = {'name': 'paragraph', 'pattern': r'(?:\n\n|\A)(?!# |\* |\- |\d+\. |\+ |```|<table|<ul|<ol|<h[1-6]|===|\[|\!\[|---|<hr|\|)(.*?)(?=\n|\Z)'}
    update_first_pattners(FIRST_PATTERNS)
    update_patterns(PATTERNS_2)
    update_patterns(PATTERNS_3)
    
    # Sort parsed elements by their start position
    parsed_elements.sort(key=lambda x: x["start"])
    for i, element in enumerate(parsed_elements):
        element['index'] = i

    return parsed_elements, remaining_content
    
def compare_indices(prev_indices: List[Dict[str, any]], last_indices: List[Dict[str, any]]):
    keys = ['type', 'content', 'index']
    
    def dict_to_tuple(d: Dict[str, any]) -> Tuple:
        new_d = {key:d[key] for key in keys}
        return tuple(sorted(new_d.items()))

    prev_set = set(dict_to_tuple(element) for element in prev_indices)
    last_set = set(dict_to_tuple(element) for element in last_indices)
    
    added = last_set - prev_set
    removed = prev_set - last_set
    
    added = [dict(element) for element in added]
    removed = [dict(element) for element in removed]

    return added, removed

def remove(removed: List[Dict[str, any]], to_indices: List[Dict[str, any]]):
    target_indices = [item['index'] for item in removed]
    for index in target_indices:
        for item in to_indices:
            if item['index'] == index:
                to_indices.remove(item)
                
def add(added: List[Dict[str, any]], to_indices: List[Dict[str, any]]):
    for item in added:
        to_indices.append(item)
    to_indices.sort(key=lambda x: x['index'])
    return to_indices

def rebuild(to_indices: List[Dict[str, any]]) -> str:
    result = ''
    for item in to_indices:
        result += item['content'] + '\n\n'
    return result
    
def translate_markdown(added: List[Dict[str, any]], from_lang: str, to_lang_list: List[str]):
    LANG_MAPPER = {'en': 'en', 'ja': 'ja', 'ko': 'ko', 'th': 'th', 'zh': 'zh-hans', 'zh-Hant': 'zh-hant'}
    mapped_to_lang_list = []
    
    added_dict = {key : None for key in to_lang_list}
    
    for i, to_lang in enumerate(to_lang_list):
        added_dict[to_lang] = copy.deepcopy(added)
        mapped_to_lang_list.append(LANG_MAPPER[to_lang])
        
    for i, item in enumerate(added):
        if item['type'] == 'code_block':
            continue
        elif item['type'] == 'code_tabs':
            continue
        else:
            # Call new translate_text and get specific language result
            translations = translate_text(
                item['content'], 
                from_lang, 
                mapped_to_lang_list,
            )
            
            for to_lang in to_lang_list:
                added_dict[to_lang][i]['content'] = translations[LANG_MAPPER[to_lang]]
    return added_dict

def check_remaining(remaining_content: str):
    if remaining_content.strip().replace('<br>', '').replace('<br/>', '').replace('<br />', '').strip() != '':
        raise ValueError(f"Remaining content found in the markdown file: {remaining_content}")

def check_differences(prev_indices: List[Dict[str, any]], last_indices: List[Dict[str, any]]):
    # 1. check length
    if len(prev_indices) != len(last_indices):
        raise ValueError(f"Length of the source and target indices do not match: {len(prev_indices)} vs {len(last_indices)}")
    
    # 2. check each item
    for i, (prev_item, last_item) in enumerate(zip(prev_indices, last_indices)):
        if prev_item['type'] != last_item['type']:
            raise ValueError(f"Source and target indices do not match at index {i}:\nSource: {prev_item}\nTarget: {last_item}")
    return

def get_indices(path, commits, order='before'):
    if order == 'before':
        md = ray_tools_git.get_file_before_commits(path, commits)
    elif order == 'after':
        md = ray_tools_git.get_file_after_commits(path, commits)
    else:
        raise ValueError(f"Invalid order: {order}")
    indices, remaining = parse_markdown(md)
    check_remaining(remaining)
    return indices, md

def translate(source_md_path, from_lang, to_lang_list, commits):    
    from_prev_indices, _ = get_indices(source_md_path, commits, order='before')
    from_last_indices, _ = get_indices(source_md_path, commits, order='after')
    
    added, removed = compare_indices(from_prev_indices, from_last_indices)
    
    results = {key : {} for key in to_lang_list}
    
    for to_lang in to_lang_list:
        # for source_md_path in source_md_paths:
        to_md_path = source_md_path.replace(f'/{from_lang}/', f'/{to_lang}/')
        to_prev_indices, to_prev_md = get_indices(to_md_path, commits, order='before')

        check_differences(from_prev_indices, to_prev_indices)        
        remove(removed, to_prev_indices)
        
        results[to_lang]['to_md_path'] = to_md_path
        results[to_lang]['to_prev_md'] = to_prev_md
        results[to_lang]['to_prev_indices'] = to_prev_indices
        
    # Translate the added content
    added_dict = translate_markdown(added, from_lang, to_lang_list)
    
    for to_lang in to_lang_list:
        results[to_lang]['to_last_indices'] = add(added_dict[to_lang], results[to_lang]['to_prev_indices'])
        results['translation'] = rebuild(results[to_lang]['to_last_indices'])
    
        # 결과를 다시 parsing해서 영문본과 다국어본 구조를 비교해야 함
        result_indices, remaining_result = parse_markdown(results['translation'])
        check_remaining(remaining_result)
        check_differences(from_last_indices, result_indices)
    
        to_md_file_path = os.path.join(BASE_PATH, results[to_lang]['to_md_path'])
        results['translation'] = results['translation'].strip()
        ray_tools.write_md_file(to_md_file_path, results['translation'])
        
def main():
    # from_lang = 'en'
    # to_lang_list = ['zh', 'zh-Hant', 'ja', 'th']
    from_lang = 'ko'
    to_lang_list = ['en']
    feature_branch_name = 'GCPPDG-701'
    base_branch_name = 'master'
    
    # # branch끼리 비교해서 commit 추출
    # commits = ray_tools_git.get_diff_commits_between_branches_without_merge_commits(feature_branch_name, base_branch_name)
    # if not commits:
    #     raise Exception(f"No different commits found")
    
    # MR id를 사용해 commit 추출
    mr_id = 76
    commits = ray_tools_git.get_mr_commits(mr_id)
    commits = [commit['id'] for commit in commits]
    if not commits:
        raise Exception(f"No different commits found")
    
    source_md_path = 'docs/ko/releases/crossplay-launcher/index.md'
    translate(source_md_path, from_lang, to_lang_list, commits)
    
if __name__ == "__main__":
    main()