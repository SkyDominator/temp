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

load_dotenv("C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/llm/env/data.env")
GROQ_CLOUD_API_KEY = os.getenv('GROQ_CLOUD_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

MODEL_OPTIONS = {
    'google': ['gemini-1.5-flash'],
    'groq': ['llama-3.1-70b-versatile']
}

def post_translation(content: str, lang: Literal['en', 'ko', 'ja', 'zh', 'zh-Hant', 'th']) -> str:
    if lang == 'en':
        content = ray_tools.apply_sentence_case(content)

    @ray_tools.do_except_on_codeblocks
    def bold_md_to_html(content):
        return ray_tools.bold_md_to_html(content)
    content = bold_md_to_html(content)
    
    @ray_tools.do_except_on_codeblocks
    def italic_md_to_html(content):
        return ray_tools.italic_md_to_html(content)
    content = italic_md_to_html(content)

    return content

def translate_text(text: str, model: "Model", to_lang: str) -> str:
    def _split_and_generate_translation(content: str) -> str:        
        content_chunks = ray_tools.recursive_split(content, model.count_tokens, model.OUTPUT_LIMIT)
        processed_chunks = [model.generate_translation(chunk).text for chunk in content_chunks]
        return ''.join(processed_chunks)
    
    @ray_tools.do_except_on_codeblocks
    def _generate_translation(content: str):
        total_tokens = model.count_tokens(content)
        if total_tokens >= model.OUTPUT_LIMIT:
            translated_content = _split_and_generate_translation(content)
        else:
            translated_content = model.generate_translation(content)
        return translated_content
    
    final_prompt = PROMPT.TR_PROMPTS[to_lang] + text
    translated_content = _generate_translation(final_prompt)
    translated_content = post_translation(translated_content, to_lang)
    return translated_content

class Model:
    def __init__(self, platform: str, model_name: str):
        if platform not in MODEL_OPTIONS:
            raise ValueError(f"Model platform must be one of {list(MODEL_OPTIONS.keys())}")
        if model_name not in MODEL_OPTIONS[platform]:
            raise ValueError(f"Model name must be one of {MODEL_OPTIONS[platform]}")
        self.platform = platform
        self.model_name = model_name
        self.load_ai_model()
        
    def load_ai_model(self) -> any:
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
            self.MODEL = genai.GenerativeModel(self.model_name)
            self.INPUT_LIMIT = 128000
            self.OUTPUT_LIMIT = 8192
            self.RPM_LIMIT = 15
            
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