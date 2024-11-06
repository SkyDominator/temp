

import google.generativeai as genai
import os
import re
import prompt as PROMPT
import sys
sys.path.append('C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/')
import common.ray_tools as ray_tools
from typing import Callable, Literal 
from functools import wraps
from dotenv import load_dotenv

load_dotenv(r'C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/llm/env/data.env')
GROQ_CLOUD_API_KEY = os.getenv('GROQ_CLOUD_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

        
def post_translation(content: str, lang:Literal['en', 'ko', 'ja', 'zh', 'zh-Hant', 'th']) -> str:
    if lang == 'en':
    # Apply sentence case to markdown headings
        content = ray_tools.apply_sentence_case(content)

    # Format bold text
    @ray_tools.do_except_on_codeblocks
    def bold_md_to_html(content):
        return ray_tools.bold_md_to_html(content)
    content = bold_md_to_html(content)
    
    # Format italic text
    @ray_tools.do_except_on_codeblocks
    def italic_md_to_html(content):
        return ray_tools.italic_md_to_html(content)
    content = italic_md_to_html(content)

    return content

def translate_multiple_files(root_path: str, **kwargs) -> None:
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
        translate_file(file_path, **kwargs)
        print("======Finished Translation:\n", file_path, "\n======")


def translate_file(source_path: str, model:"Model", **kwargs) -> None:
    """
    Translates the content of a Markdown file located at the given path.
    Args:
        path (str): The path to the Markdown file. 각 영문 마크다운 파일은 한글 콘텐츠로 initialize 되어 있어야 함.
    Returns:
        None: This function does not return any value.
    Raises:
        FileNotFoundError: If the file at the given path does not exist.
        PermissionError: If the file at the given path cannot be opened due to insufficient permissions.
    """
    def _read_translate_write(f_translate: Callable[[str, str], str]) -> Callable[[str, str], None]:
        @wraps(f_translate)
        def wrapper(source_path: str, to_lang: str):
            # Get from_lang
            match = re.search(r'devsite_mk\\docs\\([A-Za-z]+?)\\', source_path)
            if match:
                from_lang = match.group(1)
            else:
                raise ValueError(f"Invalid source_path: {source_path}")
            
            # Get target_path
            target_path = source_path.replace(f'docs\\{from_lang}\\', f'docs\\{to_lang}\\')
            # Load source md file
            md = ray_tools.read_md_file(source_path)
            
            LANGS = {'en':'English', 'ko':'Korean', 'ja':'Japanese', 'zh':'Simplified Chinese', 'zh-Hant':'Traditional Chinese', 'th':'Thai'}
            print(f"\nTranslating {LANGS[from_lang]} to {LANGS[to_lang]}...")
            
            try:
                translated_content = f_translate(md, to_lang)
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
            ray_tools.write_md_file(target_path, translated_content)
        return wrapper
        
    def _split_and_generate_translation(content: str) -> str:        
        content_chunks = ray_tools.recursive_split(content, model.count_tokens, model.OUTPUT_LIMIT)

        # Process each chunk
        processed_chunks = [model.generate_translation(chunk).text for chunk in content_chunks]
        
        # Unite the processed chunks
        return ''.join(processed_chunks)
    
    @ray_tools.do_except_on_codeblocks
    def _generate_translation(content: str):
        total_tokens = model.count_tokens(content)
        if total_tokens >= model.OUTPUT_LIMIT:
            print(f"File: {source_path}.")
            print(f"The content is too long. The number of tokens in the prompt is {total_tokens}.")
            print("Start splitting the content and translating...")
            translated_content = _split_and_generate_translation(content)
        else:
            translated_content = model.generate_translation(content)
        return translated_content
    
    @_read_translate_write
    @ray_tools.rate_limiter(model.RPM_LIMIT)
    def _translate(md: str, to_lang: str) -> str:
        final_prompt = PROMPT.TR_PROMPTS[to_lang] + md
        translated_content = _generate_translation(final_prompt)
        translated_content = post_translation(translated_content, to_lang)
        return translated_content
        
    source_path = os.path.normpath(source_path)

    # Extract any additional keyword arguments
    en = kwargs.get('en', False)
    ja = kwargs.get('ja', False)
    zh = kwargs.get('zh', False)
    zh_Hant = kwargs.get('zh_Hant', False)
    th = kwargs.get('th', False)
        
    if en:
        _translate(source_path, 'en')
    # Then, translate the content for other languages, if necessary.
    if ja:
        _translate(source_path, 'ja')
    if zh:
        _translate(source_path, 'zh')
    if zh_Hant:
        _translate(source_path, 'zh-Hant')
    if th:
        _translate(source_path, 'th')

# ====================================================================================================

class Model:
    def __init__(self, platform:str, model_name:str):
        if platform not in ['google', 'groq']:
            raise ValueError("Model must be one of 'google' or 'groq'")
        self.platform = platform
        self.model_name = model_name
        self.load_ai_model()
        
    def load_ai_model(self) -> any:
        
        # Define token counter
        # Use Google's API to count tokens
        genai.configure(api_key=GOOGLE_API_KEY)
        tmp_model = genai.GenerativeModel('gemini-1.5-flash')
        def count_tokens_wrapper(f_count_tokens: Callable) -> Callable[[str], int]:
            @wraps(f_count_tokens)
            def wrapper(content: str) -> int:
                return f_count_tokens(content).total_tokens
            return wrapper
        self.count_tokens = count_tokens_wrapper(tmp_model.count_tokens)
        
        if self.platform == 'google':
            genai.configure(api_key=GOOGLE_API_KEY)
            # test_model = genai.GenerativeModel('gemini-pro')
            self.MODEL = genai.GenerativeModel(self.model_name)
            # NORMAL = genai.GenerativeModel('gemini-1.5-pro')
            self.INPUT_LIMIT = 128000
            self.OUTPUT_LIMIT = 8192
            # low = genai.GenerativeModel('gemini-1.0-pro')
            # RPM_LIMIT = 2 # 1.5 pro
            self.RPM_LIMIT = 15 # 1.5 flash
            
            def gen_translation_wrapper(f_generate_content: Callable) -> Callable[[str], str]:
                @wraps(f_generate_content)
                def wrapper(content: str) -> str:
                    return f_generate_content(content).text
                return wrapper
            
            self.generate_translation = gen_translation_wrapper(self.MODEL.generate_content)
            
        elif self.platform == 'groq':
            from groq import Groq
            self.MODEL = Groq(api_key=GROQ_CLOUD_API_KEY,)
            self.INPUT_LIMIT = 128000
            self.OUTPUT_LIMIT = 20000
            self.RPM_LIMIT = 30
            
            def gen_translation_wrapper(f_generate_content: Callable) -> Callable[[str], str]:
                @wraps(f_generate_content)
                def wrapper(content: str) -> str:
                    result = f_generate_content(
                        messages=[
                            {
                                "role": "system",
                                "content": "you are a professional language translator, specialized in IT technology.",
                            },
                            {
                                "role": "user",
                                "content": f"{content}",
                            }
                        ],
                        model=self.model_name,
                    )
                    return result.choices[0].message.content
                return wrapper
            
            self.generate_translation = gen_translation_wrapper(self.MODEL.chat.completions.create)
            
        else:
            raise ValueError("Model must be one of 'google' or 'groq'")
        

def main():
    
    # # Multiple Files
    # path = r'C:\Users\khy\Documents\workspace\devsite_mk\docs\ko\dev\basic-config'
    # # 1. 영문 번역
    # translate_multiple_files(path, en=True)
    # # 2. 다국어 번역
    # path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\dev\basic-config"
    # translate_multiple_files(path, ja=True, zh=True)
    
    # Single File
    path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\ko\releases\unreal5\windows.md"
    # 1. 영문 번역
    GroqModel = Model('groq', 'llama-3.1-70b-versatile')
    translate_file(path, GroqModel, en=True)
    
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
   



