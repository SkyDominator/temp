

import google.generativeai as genai
import os
import prompt as PROMPT
import sys
sys.path.append('C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/')
import common.ray_tools as ray_tools
from typing import Callable
from functools import wraps
from dotenv import load_dotenv

load_dotenv(r'C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/llm/env/data.env')
GROQ_CLOUD_API_KEY = os.getenv('GROQ_CLOUD_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


def translate_file(source_path: str, target_path:str, model:"Model", **kwargs) -> None:    
    def _split_and_generate_translation(content: str) -> str:        
        content_chunks = ray_tools.recursive_split(content, model.count_tokens, model.OUTPUT_LIMIT)

        # Process each chunk
        processed_chunks = [model.generate_translation(chunk) for chunk in content_chunks]
        
        # Unite the processed chunks
        return ''.join(processed_chunks)

    def _generate_translation(content: str):
        translated_content = _split_and_generate_translation(content)
        return translated_content
    
    @ray_tools.rate_limiter(model.RPM_LIMIT)
    def _translate(md: str, to_lang: str) -> str:
        final_prompt = md
        translated_content = _generate_translation(final_prompt)
        return translated_content
        
    source_path = os.path.normpath(source_path)
    # Extract any additional keyword arguments
    ko = kwargs.get('ko', False)
        
    if ko:
        md = ray_tools.read_md_file(source_path)
        prompt = "You are a professional English-Korean language translator, specialized in IT technology. Please translate the following English contents into Korean. The result must be in markdown format. Here comes the English source contents:\n\n" + md
        translated_text = _translate(prompt, 'ko')
    
    ray_tools.write_md_file(target_path, translated_text)
    


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
            self.OUTPUT_LIMIT = 5000
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
    path = r"C:\Users\raykim\Downloads\경력기술서_영문.md"
    target_path = r"C:\Users\raykim\Downloads\경력기술서_한글_번역본.md"
    # 1. 영문 번역
    GroqModel = Model('groq', 'llama-3.1-70b-versatile')
    translate_file(path, target_path, GroqModel, ko=True)
    
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
   



