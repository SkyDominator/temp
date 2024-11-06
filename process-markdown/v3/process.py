import re, os, sys
sys.path.append('C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/')
import common.ray_tools as ray_tools
from markdownify import markdownify as md
from typing import Callable, Literal

'''
content processors
'''


'''
Check the number of words in each markdown file, and get top k files with the most number of words.
'''
@ray_tools.do_on_multiple_files
@ray_tools.do_on_single_file
def check_page_length(content: str):
    return ray_tools.check_num_of_words(content)
    
def print_topk_pages(root_path: str, top_k:int) -> None:
    results = check_page_length(root_path)
    results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
    counter = 0
    print(f"Top {top_k} files with the most number of words:")
    for path, count in results.items():
        print(f"{path}: {count}")
        counter+=1
        if counter == top_k:
            break

'''
Fix links without trailing slash
'''
@ray_tools.do_on_multiple_files
@ray_tools.do_on_single_file
@ray_tools.do_except_codeblocks
def fix_links_without_trailing_slash(content: str, *args, **kwargs) -> str:
    patterns_without_trailing_slash = [
        r'(\[.*?\]\((\..*?[^/])\))',
        r'(\[.*?\]\((\..*?[^/])#.*?\))',
        r'(<a href="(\..*?[^/])">)',
        r'(<a href="(\..*?[^/])#.*?">)',
    ]
    
    def add_trailing_slash(match):
        full_match = match.group(1)
        link = match.group(2)
        return full_match.replace(link, link + '/')
    
    for pattern in patterns_without_trailing_slash:
        content = re.sub(pattern, add_trailing_slash, content)
    
    return content

# ray_tools.save_results(root_path, results)

'''
Convert HTML tables to markdown tables
'''
def modify_table(html_table: str) -> str:
    if 'rowspan' in html_table or 'colspan' in html_table or '<aside' in html_table:
        return html_table
    else:
        return md(html_table)

def table_html_to_md(content: str) -> str:
    return ray_tools.find_and_replace(content, modify_table, r'<table.*?</table>')

@ray_tools.do_on_multiple_files
@ray_tools.do_on_single_file
@ray_tools.do_except_on_codeblocks
def convert(content: str, *args, **kwargs) -> str:
    modified_content = table_html_to_md(content)
    return modified_content

# ray_tools.save_results(root_path, results)

'''
Check if there are any unclosed list tags in the markdown content.
'''
@ray_tools.do_on_multiple_files
@ray_tools.do_on_single_file
@ray_tools.do_except_codeblocks
def get_unclosed_list_tags(content: str, *args, **kwargs) -> list:
    stack = []
    # Regex pattern to capture unclosed ordered, unordered, and list tags
    unclosed_tag_pattern = re.compile(r'<(ul|ol|li)(\s[^>]*)?>|</(ul|ol|li)>')
    unclosed_tags = []
    
    for match in unclosed_tag_pattern.finditer(content):
        if match.group(3):  # closing tag
            tag = match.group(3)
            if stack and stack[-1] == tag:
                stack.pop()
            else:
                unclosed_tags.append(content[max(0, match.start() - 100):match.end() + 100])
        else:  # opening tag
            tag = match.group(1)
            stack.append(tag)
    
    while stack:
        # If there are still tags in the stack, it means they are unclosed
        last_unclosed_tag = stack.pop()
        last_unclosed_tag_pos = content.rfind(f'<{last_unclosed_tag}')
        unclosed_tags.append(content[max(0, last_unclosed_tag_pos - 100):last_unclosed_tag_pos + 100])
    
    return unclosed_tags

        
# li li -> li /li
# No ul/ol li /li No /ul/ol -> ul li /li /ul
#  


def main():
    path_list = [r'C:\Users\khy\Documents\workspace\devsite_mk\docs\en\dev', 
                 r'C:\Users\khy\Documents\workspace\devsite_mk\docs\en\api',
                 r'C:\Users\khy\Documents\workspace\devsite_mk\docs\en\releases',
                 r'C:\Users\khy\Documents\workspace\devsite_mk\docs\ko\dev',
                 r'C:\Users\khy\Documents\workspace\devsite_mk\docs\ko\api',
                 r'C:\Users\khy\Documents\workspace\devsite_mk\docs\ko\releases']
    
    for i, path in enumerate(path_list):
        result_path = os.path.dirname(__file__) + f'\\output_{i}'
        results = get_unclosed_list_tags(path)
        ray_tools.save_results_to_file(path, result_path, results)

main()