import os, re
from functools import wraps
from typing import Callable
import time
from collections import deque
from threading import Lock
from typing import Callable, Dict, Any, List, Tuple

'''
file processor functions
'''
def read_md_file(abs_path:str) -> str:
    abs_path = os.path.normpath(abs_path)
    with open(abs_path, 'r', encoding='utf-8') as md_file:
        md = md_file.read()
        return md

def write_md_file(abs_path:str, content:str) -> None:
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, 'w+', encoding='utf-8') as md_file:
        md_file.write(content)

def get_all_md_file_paths(abs_root_path: str) -> list[str]:
    # Return a list of all markdown file absolute paths in the root directory
    md_file_paths = []
    for root, dirs, files in os.walk(abs_root_path):
        for file in files:
            if file.endswith('.md'):
                path = os.path.normpath(os.path.join(root, file))
                md_file_paths.append(path)
    return md_file_paths

def do_on_multiple_files(f: Callable[[str], any]) -> Callable[[str], dict[str, any]]:
    @wraps(f)
    def wrapper(root_path: str) -> dict[str, str]:
        # Get all markdown file paths
        md_file_paths = get_all_md_file_paths(root_path)
        results = {}
        # Process each markdown file
        for md_file_path in md_file_paths:
            result = f(md_file_path)
            results[md_file_path] = result
        return results
    return wrapper

def async_do_on_multiple_files(f: Callable[[str], any]) -> Callable[[str], dict[str, any]]:
    @wraps(f)
    async def wrapper(root_path: str) -> dict[str, str]:
        # Get all markdown file paths
        md_file_paths = get_all_md_file_paths(root_path)
        results = {}
        # Process each markdown file
        for md_file_path in md_file_paths:
            result = await f(md_file_path)
            results[md_file_path] = result
        return results
    return wrapper
    
def do_on_single_file(f: Callable[[str], any]) -> Callable[[str], any]:
    @wraps(f)
    def wrapper(file_path: str) -> any:
        content = read_md_file(file_path)
        # Process content
        result = f(content)
        return result
    return wrapper

def save_results(root_path:str, results: dict[str, str]):
    for path, content in results.items():
        write_md_file(path, content)

def save_results_to_file(file_path:str, result_path:str, results: dict[str, list[str]]):
    result_file_path = os.path.join(result_path, 'check_result.txt')
    # result_dir = os.path.dirname(result_path)
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    
    with open(result_file_path, 'w', encoding='utf-8') as result_file:
        result_file.write(f'PATH: {file_path}\n\n\n')
        for key, file_results in results.items():
            result_file.write(f"Key: {key}\n")
            for result in file_results:
                result_file.write(f"{result} \n")
                result_file.write("--------------------------------------------------\n")
            result_file.write('\n\n')

def do_create_report(f: Callable[[str], Dict[str, Any]]):
    # f MUST BE the decorated function with do_on_multiple_files
    @wraps(f)
    def wrapper(root_path:str, result_path:str, results:dict):
        result_file_path = os.path.join(result_path, 'result.txt')
        if not os.path.exists(result_path):
            os.makedirs(result_path)
        
        with open(result_file_path, 'w', encoding='utf-8') as result_file:
            result_file.write(f'ROOT DIRECTORY: {root_path}\n\n\n')
            for path, result in results.items():
                result_file.write(f"FILE: {path}\n")
                f(result_file, result)
    return wrapper
'''
Usage:
@do_on_multiple_files
@write_single_file
def process(content):
    # Process content here
    return content
'''

'''
content checker functions
'''



def check_num_of_words(content: str) -> int:
    words = content.split()
    num_of_words = len(words)
    return num_of_words
'''
usage:
@check_single_file
def check_num_of_words(content: str) -> str:
    words = content.split()
    num_of_words = len(words)
    return num_of_words
'''

'''
content processor functions
'''

# apply sentence case to markdown headings.
def apply_sentence_case(content : str) -> str:
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

def do_except_codeblocks(f: Callable[[str], str]) -> Callable[[str], any]:
    @wraps(f)
    def wrapper(content: str, *args, **kwargs) -> str:
        # Find all code blocks
        code_blocks = re.findall(r'```.*?```', content, flags=re.DOTALL)
        
        # Replace code blocks with placeholders
        placeholders = [f"__CODE_BLOCK_{i}__" for i in range(len(code_blocks))]
        for placeholder, code_block in zip(placeholders, code_blocks):
            content = content.replace(code_block, placeholder)
        
        # Apply the function to the content without code blocks
        result = f(content)
        return result
    
    return wrapper

def do_except_on_contents_block_with_pattern_list(pattern_list: List[str]) -> Callable[[Callable[[str], str]], Callable[[str], str]]:
    def decorator(f: Callable[[str], str]) -> Callable[[str], str]:
        @wraps(f)
        def wrapper(content: str, *args, **kwargs) -> str:
            # Find all blocks for each regex pattern
            for i, pattern in enumerate(pattern_list):
                # Replace blocks with placeholders
                content = content.replace(pattern, f"__EXCEPT_CONTENTS_OBJECT_{i}_")
                
            # Apply the function to the content without blocks
            modified_content = f(content)
                        
            for i, pattern in enumerate(pattern_list):
                # Replace blocks with placeholders
                modified_content = modified_content.replace(f"__EXCEPT_CONTENTS_OBJECT_{i}_", pattern)
            
            return modified_content
        return wrapper
    return decorator


def do_except_on_contents_block_with_regex_dict(regex_pattern_dict: Dict[str, str]) -> Callable[[Callable[[str], str]], Callable[[str], str]]:
    def decorator(f: Callable[[str], str]) -> Callable[[str], str]:
        @wraps(f)
        def wrapper(content: str, *args, **kwargs) -> str:
            all_blocks = []
            all_placeholders = []
            
            # Find all blocks for each regex pattern
            for i, key in enumerate(regex_pattern_dict):
                if key == 'markdown-table':
                    blocks = re.findall(regex_pattern_dict[key], content, flags=re.MULTILINE)
                else:
                    blocks = re.findall(regex_pattern_dict[key], content, flags=re.DOTALL)
                
                placeholders = [f"__EXCEPT_CONTENTS_OBJECT_{i}_{j}__" for j in range(len(blocks))]
                all_blocks.extend(blocks)
                all_placeholders.extend(placeholders)
                
                # Replace blocks with placeholders
                for placeholder, block in zip(placeholders, blocks):
                    content = content.replace(block, placeholder)
            
            # Apply the function to the content without blocks
            modified_content = f(content, *args, **kwargs)
            
            # Restore the blocks
            for placeholder, block in zip(all_placeholders, all_blocks):
                modified_content = modified_content.replace(placeholder, block)
            
            return modified_content
        return wrapper
    return decorator

def do_except_on_codeblocks(f: Callable[[str], str]) -> Callable[[str], str]:
    @wraps(f)
    def wrapper(content: str, *args, **kwargs) -> str:
        # Find all code blocks
        code_blocks = re.findall(r'```.*?```', content, flags=re.DOTALL)
        
        # Replace code blocks with placeholders
        placeholders = [f"__CODE_BLOCK_{i}__" for i in range(len(code_blocks))]
        for placeholder, code_block in zip(placeholders, code_blocks):
            content = content.replace(code_block, placeholder)
        
        # Apply the function to the content without code blocks
        modified_content = f(content, *args, **kwargs)
        
        # Restore the code blocks
        for placeholder, code_block in zip(placeholders, code_blocks):
            modified_content = modified_content.replace(placeholder, code_block)
        
        return modified_content
    
    return wrapper

# **bbb** -> <b>bbb</b>
def bold_md_to_html(content: str) -> str:
    # Define the pattern to match bold text
    pattern = r'(?<!\*)\*\*([^ ][^*]+?[^ ])\*\*(?!\*)'

    # Define the replacement function to format bold text
    def replace(match):
        text = match.group(1)
        return f'<b>{text}</b>'

    # Apply the replacement function to all bold text
    result = re.sub(pattern, replace, content, flags=re.MULTILINE)
    return result

# *bbb* -> <i>bbb</i>
def italic_md_to_html(content: str) -> str:
    # Define the pattern to match bold text
    pattern = r'(?<!\*)\*([^ ][^*]+?[^ ])\*(?!\*)'
    
    # Define the replacement function to format bold text
    def replace(match):
        text = match.group(1)
        return f'<i>{text}</i>'

    # Apply the replacement function to all bold text
    result = re.sub(pattern, replace, content, flags=re.MULTILINE)
    return result

def italic_html_to_md(content: str) -> str:
    modified_content = re.sub(r'<i>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)
    return modified_content

def bold_html_to_md(content: str) -> str:
    modified_content = re.sub(r'<b>(.*?)</b>', r'**\1**', content, flags=re.DOTALL)
    return modified_content

def find_and_replace(content: str, f: Callable, regex_pattern: r'str') -> str:
    objects = re.findall(regex_pattern, content, flags=re.DOTALL)
    for obj in objects:
        modified_obj = f(obj)  # Example modification
        content = content.replace(obj, modified_obj)
    return content

# Calculate non-intervals
def calculate_non_intervals(content: str, intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    '''
    # Example usage
    example_string = "This is a sample string with some intervals."
    example_intervals = [(5, 7), (11, 17)]
    example_non_intervals = calculate_non_intervals(example_string, example_intervals)
    print("Example non-intervals:", example_non_intervals)
    '''
    non_intervals = []
    current_index = 0

    for start, end in sorted(intervals):
        if current_index < start:
            non_intervals.append((current_index, start))
        current_index = max(current_index, end)

    if current_index < len(content):
        non_intervals.append((current_index, len(content)))

    return non_intervals
    
def get_non_overlapping_intervals(start_indices, end_indices):
    '''
    # _start_indices format
    # (116, 208, 4917, 5381, 6014)
    # _end_indices format
    # (184, 276, 4985, 5422, 6082)
    
    # merged_indices format
    # [(116, 184), (208, 276), (672, 4521), (4917, 4985), (5226, 7345)]
    '''
    intervals = sorted(zip(start_indices, end_indices))
    merged_intervals = []
    
    for start, end in intervals:
        if not merged_intervals or start > merged_intervals[-1][1]:
            merged_intervals.append((start, end))
        else:
            merged_intervals[-1] = (merged_intervals[-1][0], max(end, merged_intervals[-1][1]))
    
    return merged_intervals

def format_headings(content: str) -> str:
    
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

def remove_code_blocks(content: str) -> str:
    modified_content = re.sub(r'```.*?```', '', content, flags = re.DOTALL)
    return modified_content

def split_by_heading(text: str) -> list:
    # Split by markdown headings
    parts = re.split(r'(^#+ .*$)', text, flags=re.MULTILINE)
    if len(parts) <= 1:
        return [text]  # No headings found, return the original text
    
    # Combine the parts into chunks
    chunks = [parts[i] + parts[i + 1] for i in range(0, len(parts) - 1, 2)] + [parts[-1]]
    
    # Find the approximate middle point
    total_length = sum(len(chunk) for chunk in chunks)
    mid_point = total_length // 2
    
    # Adjust the mid_point to be closer to an actual heading
    current_length = 0
    split_index = 0
    for i, chunk in enumerate(chunks):
        current_length += len(chunk)
        if current_length >= mid_point:
            split_index = i
            break
    # Split the chunks into two near-equal parts
    return [''.join(chunks[:split_index + 1]), ''.join(chunks[split_index + 1:])]

def split_by_empty_line(text: str) -> list:
    # Split by empty lines
    parts = text.split('\n\n')
    total_length = len(parts)
    
    # Find the approximate middle point
    mid_point = total_length // 2
    
    # Adjust the mid_point to be closer to an empty line
    if total_length > 1:
        left_length = sum(len(part) for part in parts[:mid_point])
        right_length = sum(len(part) for part in parts[mid_point:])
    
    # Adjust mid_point to minimize the difference in length between the two halves
    while mid_point > 0 and abs(left_length - right_length) > abs(left_length + len(parts[mid_point]) - right_length - len(parts[mid_point])):
        mid_point -= 1
        left_length += len(parts[mid_point])
        right_length -= len(parts[mid_point])
    
    return ['\n\n'.join(parts[:mid_point]), '\n\n'.join(parts[mid_point:])]


def split_by_period(content: str) -> list[str]:
    # Remove code blocks and tables from the content
    plain_text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    plain_text = re.sub(r'\|.*?\|', '', plain_text)
    plain_text = re.sub(r'<table>.*?<\/table>', '', plain_text, flags=re.DOTALL)

    # Find the middle index of the plain text
    middle_index = len(plain_text) // 2

    # Find the nearest period to the middle index in the plain text
    left_period_index = plain_text.rfind('.', 0, middle_index)
    right_period_index = plain_text.find('.', middle_index)

    # Choose the period that is closest to the middle index
    if left_period_index == -1 and right_period_index == -1:
        # No period found, split at the middle index
        split_index = middle_index
    elif left_period_index == -1:
        # No period found on the left, split at the right period
        split_index = right_period_index + 1
    elif right_period_index == -1:
        # No period found on the right, split at the left period
        split_index = left_period_index + 1
    else:
        # Both periods found, choose the closest one
        if middle_index - left_period_index <= right_period_index - middle_index:
            split_index = left_period_index + 1
        else:
            split_index = right_period_index + 1

    # Find the corresponding split index in the original content
    original_split_index = content.find(plain_text[split_index - 1]) + 1

    # Split the string into two parts
    part1 = content[:original_split_index].strip()
    part2 = content[original_split_index:].strip()

    return [part1, part2]

def recursive_split(content: str, f_threshold_checker: Callable, threshold: int) -> list[str]:
    
    def split(content: str) -> list[str]:
        chunks = split_by_heading(content)
        if len(chunks) == 1:  # No headings found, split by empty line
            chunks = split_by_empty_line(content)
        if len(chunks) == 1:  # Still only one chunk, split in half manually
            chunks = split_by_period(content)
        if len(chunks) == 1:
            raise ValueError("Unable to split content")
        return chunks

    def helper(content: str, depth: int = 0) -> list[str]:
        if depth > 16:  # Set the maximum recursion depth to 16. 2^16 = 65536 tokens
            raise ValueError("Exceeded maximum recursion depth")
        if f_threshold_checker(content) <= threshold:
            return [content]
        chunks = split(content)
        result = []
        for chunk in chunks:
            if chunk == "":  # Skip empty chunks
                continue
            if f_threshold_checker(chunk) > threshold:
                result.extend(helper(chunk, depth + 1))
            else:
                result.append(chunk)
        return result

    final_result = helper(content)
    print(f"Split into: {len(final_result)} parts")
    for i, part in enumerate(final_result):
        print(f"Part {i + 1}: {f_threshold_checker(part)} tokens")
    return final_result

'''
link processor functions
'''
def parse_link(link: str) -> dict[str]:
    link = link.lower()
    link = link.strip()
    result = { 'link': link, 'type': 'external' if link.startswith('http') else 'internal' }
    
    match link:
        case _ if '.md' in link:
            anchor_check = link.split('.md#')
            match len(anchor_check):
                case 2:
                    result['anchor'] = None if anchor_check[1] == '' else anchor_check[1]
                    result['link'] = anchor_check[0] + '.md'
                case 1:
                    return result
                case _:
                    raise ValueError(f"Unexpected link format: {link}")
            return result
        case _ if link.startswith('#'):
            result['anchor'] = link[1:]
            result['type'] = 'same-page'
            return result
        case _ if result['type'] == 'external':
            return result
        case _ if link.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            result['type'] = 'image'
            return result
        case _ if link.endswith('.pdf'):
            result['type'] = 'pdf'
            return result
        case _ if link.endswith(('.zip', '.tar', '.tar.gz', '.tar.bz2', '.tgz', '.gz', '.bz2', '.7z', '.rar')):
            result['type'] = 'archive'
            return result
        case _:
            raise ValueError(f"Unexpected link format: {link}")

'''
path processor functions
'''
def resolve_relative_link(file_path: str, relative_link: str) -> str:
    # Normalize the file path and relative link
    file_path = os.path.normpath(file_path)
    relative_link = os.path.normpath(relative_link)
    
    # Get the directory of the file
    file_dir = os.path.dirname(file_path)
    
    # Join the directory with the relative link to get the path
    path = os.path.join(file_dir, relative_link)
    
    # Normalize the absolute path
    path = os.path.normpath(path)
    
    return path

'''
handling request limits
'''
def rate_limiter(max_requests_per_minute: int):
    interval = 60.0 / max_requests_per_minute
    lock = Lock()
    request_times = deque()

    def decorator(f: Callable):
        @wraps(f)
        def do_with_request_limit(*args, **kwargs):
            with lock:
                current_time = time.time()
                while request_times and current_time - request_times[0] > 60:
                    request_times.popleft()
                
                if len(request_times) >= max_requests_per_minute:
                    sleep_time = interval - (current_time - request_times[0])
                    if sleep_time > 0:
                        print("Rate limit will be exceeded. Sleeping for", sleep_time, "seconds")
                        time.sleep(sleep_time)
                    request_times.popleft()
                
                request_times.append(time.time())
                return f(*args, **kwargs)
        
        return do_with_request_limit
    
    return decorator
