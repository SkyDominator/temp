

import google.generativeai as genai
import os
import re
import prompt as PROMPT
import sys
sys.path.append('C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/')
import common.ray_tools as ray_tools
from typing import Callable
from functools import wraps

from dotenv import load_dotenv
import requests
import json
import time
from typing import List

load_dotenv(r'C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/llm/env/data.env')
GPT4_O_MINI_APP_KEY = os.getenv('GPT4-O-MINI-APP-KEY')
GPT4_O_MINI_APP_SIGNATURE = os.getenv('GPT4-O-MINI-APP-SIGNATURE')

NO_TRANSLATION = {
    "white-labeling-1": r'%% brand_name %%', 
    "white-labeling-2": r'%% project_name %%',
    # "code-block": r'```.*?```',
    # "markdown-table": r'(?:(?:^\s*\|.+\|[ \t]*$\n?)+(?:^\s*\|[-:| ]+\|[ \t]*$\n?)?(?:^\s*\|.+\|[ \t]*$\n?)+)',
    # "html-table": r'<table.*?/table>',
}

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

def translate_text_wrapper(*args, **kwargs):
    if kwargs.get('regex_dict', False):
        @ray_tools.do_except_on_contents_block_with_regex_dict(kwargs['regex_dict'])
        def _generate_translation(*args, **kwargs):
            return translate_text(*args, **kwargs)
    elif kwargs.get('pattern_list', False):
        @ray_tools.do_except_on_contents_block_with_pattern_list(kwargs['pattern_list'])
        def _generate_translation(*args, **kwargs):
            return translate_text(*args, **kwargs)
    else:
        @ray_tools.do_except_on_codeblocks
        def _generate_translation(*args, **kwargs):
            return translate_text(*args, **kwargs)
    translations = _generate_translation(*args, **kwargs)
    translations = post_translation(translations)
    return translations

def post_translation(translations: dict[str, str]) -> dict[str, str]: 
    # Apply sentence case to markdown headings
    if translations.get('en', False):
        translations['en'] = ray_tools.apply_sentence_case(translations['en'])

    # Format bold text
    @ray_tools.do_except_on_codeblocks
    def bold_md_to_html(content, *args, **kwargs):
        return ray_tools.bold_md_to_html(content)
    
    for lang in translations.keys():
        translations[lang] = bold_md_to_html(translations[lang])
    
    # Format italic text
    @ray_tools.do_except_on_codeblocks
    def italic_md_to_html(content, *args, **kwargs):
        return ray_tools.italic_md_to_html(content)
    
    for lang in translations.keys():
        translations[lang] = italic_md_to_html(translations[lang])

    return translations

def translate_multiple_files(root_path: str, to_lang_list: List[str], **kwargs) -> None:
    """
    Translates multiple markdown files from English to Korean.
    Args:
        path (str): The path to the folder containing English markdown files. 
        영문 마크다운 파일이 담긴 폴더 path이어야 함.
    Returns:
        None
    """ 
    md_file_paths = ray_tools.get_all_md_file_paths(root_path)
    
    for file_path in md_file_paths:
        print("======Start Translation:\n", file_path, "\n======")
        translate_file(file_path, to_lang_list, **kwargs)
        print("======Finished Translation:\n", file_path, "\n======")

def read_translate_write(f_translate: Callable[[str, str], str]) -> Callable[[str, str], None]:
    @wraps(f_translate)
    def wrapper(source_path, to_lang_list, **kwargs):
        # Get from_lang
        match = re.search(r'devsite_mk\\docs\\([A-Za-z]+?)\\', source_path)
        if match:
            from_lang = match.group(1)
        else:
            raise ValueError(f"Invalid source_path: {source_path}")
        
        # Get text
        text = ray_tools.read_md_file(source_path)
        
        target_paths = {to_lang : '' for to_lang in to_lang_list}
        for to_lang in to_lang_list:
            target_paths[to_lang] = source_path.replace(f'docs\\{from_lang}\\', f'docs\\{to_lang}\\')
        
        LANGS = {'en':'English', 'ko':'Korean', 'ja':'Japanese', 'zh':'Simplified Chinese', 'zh-Hant':'Traditional Chinese', 'th':'Thai'}
        print(f"\nTranslating {LANGS[from_lang]} to {LANGS[to_lang]}...")
        
        try:
            translations = f_translate(text, from_lang, to_lang_list, **kwargs)
        except ValueError as e:
            if 'Error-001' in str(e):
                print(f"File: {source_path}.")
                print(e)
                exit()
            elif 'Error-000' in str(e):
                print(f"File: {source_path}.")
                print(e)
                exit()
            else:
                print(f"File: {source_path}.")
                print(e)
                exit()
        print(f"Translation from {LANGS[from_lang]} to {LANGS[to_lang]} is complete.")
        # write translated content to target_path
        for to_lang in target_paths:
            ray_tools.write_md_file(target_paths[to_lang], translations[to_lang])
    return wrapper
    
def translate_file(source_path: str, to_lang_list: List[str], **kwargs) -> None:
    @read_translate_write
    def _translate(*args, **kwargs) -> str:
        return translate_text_wrapper(*args, **kwargs)
        
    source_path = os.path.normpath(source_path)
    _translate(source_path, to_lang_list, **kwargs)
        

def main():
    
    # # Multiple Files
    # path = r'C:\Users\khy\Documents\workspace\devsite_mk\docs\ko\dev\basic-config'
    # # 1. 영문 번역
    # translate_multiple_files(path, en=True)
    # # 2. 다국어 번역
    # path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\dev\basic-config"
    # translate_multiple_files(path, ja=True, zh=True)
    
    # Single File
    path = r"C:\Users\raykim\Documents\workspace\devsite_mk\docs/ko/releases/crossplay-launcher/index.md"
    # TARGET_LANGS = ['ja', 'ko', 'th', 'zh', 'zh-Hant']  # List of target languages
    TARGET_LANGS = ['en']  # List of target languages
    # 1. 영문 번역
    # prompt = True는 작동하지 않는 것 같음.
    translate_file(path, TARGET_LANGS, regex_dict=NO_TRANSLATION)
    
    # 2. 다국어 번역
    # path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\dev\analytics\hive-send-log\fluentd\fluentd-docker-guide.md"
    # translate_file(path, ja=True, zh=True, zh_Hant=True, th=True)
    
    # From English Source Single File
    # path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\api\hive-server-api\billing\verify-subscription.md"
    # path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\api\hive-server-api\billing\hiveitem-v2.md"
    # path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\dev\basic-config\index.md"
    # GroqModel = Model('groq', 'llama-3.1-70b-versatile')
    # translate_file(path, ja=True, zh=True, zh_Hant=True, th=True)
    # translate_file(path, GroqModel, zh=True)

    # # From Korean Source Single File
    # # path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\api\hive-server-api\billing\verify-subscription.md"
    # path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\ko\api\hive-server-api\billing\hiveitem-v2.md"
    # # translate_file(path, ja=True, zh=True, zh_Hant=True, th=True)
    # translate_file(path, en=True)
    
    # Very long single file
    # path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\ko\api\hive-api\resultapicode_authv4.md"

if __name__ == '__main__':
    main()
   



