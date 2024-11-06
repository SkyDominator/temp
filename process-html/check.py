"""
Process Markdown Files
This script processes markdown files by applying various modifications to the content. It includes functions to process code blocks and markdown headings. The script can process a single file or multiple files in a given directory.
Functions:
- process_code_blocks(content: str) -> str: Processes code blocks in the content by converting HTML tags to markdown syntax.
- process_headings(content: str) -> str: Applies sentence case to markdown headings in the content.
- process_single_file(file_path): Processes a single markdown file by reading the content, applying modifications, and writing the modified content back to the file.
- get_all_md_file_paths(dir) -> List[str]: Retrieves all markdown file paths in a given directory.
- process_multiple_files(path): Processes multiple markdown files in a given directory by calling the process_single_file function for each file.
- main(): The main function that orchestrates the processing of markdown files in multiple directories.
Usage:
1. Modify the paths list in the main function to specify the directories containing the markdown files to be processed.
2. Run the script to process the markdown files.

Note: 
1. This script assumes that the markdown files are encoded in UTF-8.
2. 프로세스 로직 추가, 수정, 삭제하려면 process_single_file 함수 내부를 수정해야 함.
"""

import re, os

def change_italic(content: str) -> str:
    modified_content = re.sub(r'\*(.*?)\*', r'\1', content, re.DOTALL)
    return modified_content

def change_bold(content: str) -> str:
    modified_content = re.sub(r'\*\*(.*?)\*\*', r'\1', content, re.DOTALL)
    return modified_content
    
def process_code_blocks(content: str) -> str:

    code_blocks = re.findall(r'```.*?```', content, re.DOTALL)
    modified_content = content

    for code_block in code_blocks:
       modified_code_block = change_italic(code_block)
       modified_code_block = change_bold(modified_code_block)
       
       '''
       Add more code-block process functions here
       '''
       
       modified_content = modified_content.replace(code_block, modified_code_block)

    return modified_content

def process_tables(content: str) -> str:
    
    tables = re.findall(r'<table.*?</table>', content, re.DOTALL)
    modified_content = content

    for table in tables:
       modified_table = change_italic(table)
       modified_table = change_bold(modified_table)
       
       '''
       Add more code-block process functions here
       '''
       
       modified_content = modified_content.replace(table, modified_table)

    return modified_content

def process_notes(content: str) -> str:
    
    notes = re.findall(r'<aside class\=.*?<\/aside>', content, re.DOTALL)
    modified_content = content

    for note in notes:
       modified_note = change_italic(note)
       modified_note = change_bold(modified_note)
       
       '''
       Add more code-block process functions here
       '''
       
       modified_content = modified_content.replace(note, modified_note)

    return modified_content

def process_headings(content: str) -> str:
    
    # apply sentence case to markdown headings.
    def apply_sentence_case_to_headings(content : str) -> str:
        # Define the regular expression pattern to match markdown headings
        pattern = r'(#+ )(.*)'

        # If heading_text includes some pre-defined words, do not apply sentence case on those words.
        # Define the pre-defined words
        # Can't process: 'Unreal Engine', 'Signing & Capabilities' 'SDK Manager'
        pre_defined_words = ['HiveConfig', 'PC', 'OS', 'API', 'SDK', 'URL', 'HTTP', 'HTTPS', 'HTML', 'CSS', 'JSON', 'XML', 'REST', 'RPC', 'JWT', 'OAuth', 'SAML', 'SSO', 'IdP', 'IAM', 'DNS', 'IP', 'TCP', 'UDP', 'BOM', 'RESTful', 'gRPC', 'Unreal', 'Unity', 'Cocos2d-x', 'Windows', 'macOS', 'Android', 'iOS', 'Facebook', 'QQ', 'VK', 'WeChat', 'Amazon', 'Firebase', 'Adjust', 'Singular', 'Google', 'Apple', 'Huawei', 'Samsung', 'Tencent', 'EDM4U', 'CocoaPods', 'ExternalDependency', 'HIVEAppDelegate', 'Swift', 'FmallocAnsi', 'Xcode', 'IAPV4Type', 'ConflictSingleViewInfo', 'ConflictViewInfo', 'HivePostProcess', 'Visual Studio', 'Google Play Games on PC', 'AndroidManifest.xml']
        pre_defined_words_low = [word.lower() for word in pre_defined_words]
        
        # Function to check if a word is in the pre-defined list
        def is_pre_defined_word(word):
            # word must be lower case
            return word in pre_defined_words_low
        
        def get_pre_defined_word(word):
            # word must be lower case
            index = pre_defined_words_low.index(word)
            return pre_defined_words[index]
            
        # Define the replacement function to apply sentence case
        # apply sentence case only if the word is not in the pre-defined list
        def replace(match):
            heading_level = match.group(1)
            heading_text = match.group(2)
            
            # First, capitalize only the first word of the heading text
            heading_text = heading_text.capitalize()
            words = heading_text.split()
            new_heading_text = []
            
            for word in words:
                word_low = word.lower()
                if is_pre_defined_word(word_low):
                    new_word = get_pre_defined_word(word_low)
                    new_heading_text.append(new_word)
                else:
                    new_heading_text.append(word)
                    
            return heading_level + ' '.join(new_heading_text)

        # Apply the replacement function to all markdown headings
        result = re.sub(pattern, replace, content, flags=re.MULTILINE)
        return result
    
    modified_content = apply_sentence_case_to_headings(content)
    
    '''
       Add more markdown-heading process functions here
    '''
    
    return modified_content


def process_single_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Process markdown code blocks
    # modified_content = process_code_blocks(content)
    
    # Process markdown headings
    # modified_content = process_headings(content)
    
    # Process HTML tables
    modified_content = process_tables(content)
    
    # Process HTML notes
    # modified_content = process_notes(content)
    '''
       Add more contents process functions here
    '''
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)

def get_all_html_file_paths(dir):
    html_file_paths = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith('.html'):
                html_file_paths.append(os.path.join(root, file))
    return html_file_paths

def process_multiple_files(path):
    # Get all markdown file paths
    html_file_paths = get_all_html_file_paths(path)

    # Check code blocks in each markdown file
    for html_file_path in html_file_paths:
        process_single_file(html_file_path)

def main():
    # Check Multiple Files
    paths = [
        r"C:/Users/khy/Documents/workspace/DevGuide/en/",
        r"C:/Users/khy/Documents/workspace/DevGuide/ko/",
        # r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\develop\overview",
        # r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\develop\basic-config",
        # r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\getting-started",
        
        # r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\develop\analytics\hive-sdk-prep",
        # r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\develop\authv4\hive-sdk-prep",
        # r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\develop\billing\hive-sdk-prep",
        # r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\develop\datastore\hive-sdk-prep",
        # r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\develop\marketing-attribution\hive-sdk-prep",
        # r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\develop\notification\hive-sdk-prep",
        # r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\develop\promotion\hive-sdk-prep"
    ]
    
    for path in paths:
        process_multiple_files(path)
    
    # # # Check Single File
    # path = r"C:\Users\khy\Documents\workspace\devsite_mk\docs\en\develop\index.md"
    # process_single_file(path)
        
main()