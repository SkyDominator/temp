import os, sys
sys.path.append("C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/common/")
import ray_tools_git
from typing import List, Dict
import shutil

BASE_PATH = os.path.normpath(r"C:\Users\raykim\Documents\workspace\devsite_mk")

def change_language(files: List[str], from_lang: str, to_lang: str):
    updated_files = []
    for file in files:
        parts = file.split('/')
        if parts[1] == from_lang:
            parts[1] = to_lang
        else:
            raise ValueError(f"File {file} does not match the expected language.\nExpected: {from_lang}, Actual: {parts[1]}")
        updated_files.append('/'.join(parts))
    return updated_files

def divide_files(files: List[str]) -> Dict[str, List[str]]:
    img_files = [file for file in files if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    yml_file = [file for file in files if file.endswith('.yml')]
    if len(yml_file) > 1:
        raise ValueError("More than one YAML file found in the changes.")
    md_files = [file for file in files if file.endswith('.md')]
    return {"img": img_files, "yml": yml_file, "md": md_files}

def copy_image_file(source_img_file: str, target_img_file: str):
    source_img_path = os.path.join(BASE_PATH, source_img_file)
    target_img_path = os.path.join(BASE_PATH, target_img_file)
    shutil.copy(source_img_path, target_img_path)
    

def main():        
    mr_id = 61
    source_files = ray_tools_git.get_gitlab_mr_changes(mr_id)
    divided_source_files = divide_files(source_files)
    
    # 이미지 처리 (구현, 테스트 완료)
    target_lang = ['en','zh', 'zh-Hant', 'ja', 'th']
    for lang in target_lang:
        target_files = change_language(source_files, 'ko', lang)    
        divided_target_files = divide_files(target_files)
        for i, source_img_file in enumerate(divided_source_files['img']):
            copy_image_file(source_img_file, divided_target_files['img'][i])
    
if __name__ == "__main__":
    main()