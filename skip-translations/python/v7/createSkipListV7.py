from bs4 import BeautifulSoup
import re
import os
import nltk
from nltk.corpus import stopwords
from decorators import process_file_or_files_in_dir

def get_stop_words():
    nltk.download('stopwords')
    stop_words = stopwords.words('english')
    return stop_words

def remove_stop_words(skiplist):
    stop_words = get_stop_words()
    
    # 커스톰 스톱 워드 추가. 커스톰 스톱 워드도 skip list에서 제거함.
    custom_stop_words = [
    'use', 'data', 'some', 'function', 'message', 'code', 'index', 'owner', 'lock', 'token', 'mint', 'currency',
    'status', 'string', 'get', 'order', 'reason', 'asynchronous', 'body', 'unicode', 'socket', 'header', 'duration',
    'page', 'paid', 'minute', 'day', 'go', 'games', 'cloud', 'docs', 'services', 'service', 'gaming', 'option',
    'remote', 'identifier', 'country', 'timezone', 'object', 'post', 'type', 'team', 'server', 'reward', 'info',
    'rank', 'send', 'log', 'chat', 'group', 'market', 'level', 'asset', 'since', 'character', 'scribe', 'gold',
    'test', 'result', 'encoding', 'sandbox', 'value', 'name', 'client', 'end', 'date', 'begin', 'target', 'account',
    'media', 'channel', 'count', 'distince', 'reduced', 'user', 'latest', 'greatest', 'visit', 'distinct',
    'modules', 'parameter', 'secondary', 'with', 'support', 'id',]
    stop_words.extend(custom_stop_words)

    lines = [line.strip() for line in skiplist if line.strip() not in stop_words]
    return lines

@process_file_or_files_in_dir
def extract_english_words(html_file_path):
    # Create output file path
    output_txt_file_path = re.sub(r'\.html', '_TR_SKIPS.txt', html_file_path)
    
    # Read the HTML content
    with open(html_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    # Remove tables
    for table in soup.find_all('table'):
        table.decompose()

    # Remove code blocks
    for code_block in soup.find_all(['code', 'pre']):
        code_block.decompose()
        
    # Remove the contents within the em tags
    for em in soup.find_all('em'):
        em.decompose()

    # Remove the contents within the b tags
    for b in soup.find_all('b'):
        b.decompose()

    # Remove the contents within the strong tags
    for strong in soup.find_all('strong'):
        strong.decompose()

    # Get text from the parsed HTML (excluding tags, attributes, and their values)
    content = soup.get_text()
    
    # Remove WordPress shortcodes
    content = re.sub(r'\[\/?su_.*?\]', '', content, flags=re.DOTALL)
    content = re.sub(r'\[\/?av_.*?\]', '', content, flags=re.DOTALL)
    content = re.sub(r'\[\/?markdown.*?\]', '', content, flags=re.DOTALL)
    content = re.sub(r'\[av_tab_container.*?\[\/av_tab_container\]', '', content, flags=re.DOTALL)
    content = re.sub(r'\[\/?caption.*?\]', '', content, flags=re.DOTALL)
    
    # Remove code snippet
    content = re.sub(r'`.*?`', '', content, flags=re.DOTALL)
    
    # Remove links
    content = re.sub(r'http[s]?://\S+', '', content)

    # Remove the combinations of English words and special characters
    content = re.sub(r'[a-zA-Z0-9]+([!@#$%^*_+=:.?\-]{1}[a-zA-Z0-9]+)+', '', content)

    # Find all English words
    # Remove Korean characters
    content = re.sub(r'[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]', '', content)
    # Get English words
    # words = re.findall(r'\b[A-Za-z]+\b', content)
    # words = re.findall(r'\b[A-Za-z]+[A-Za-z0-9]*[A-Za-z]+\b', content)
    # 영문자 2개 이상으로 시작하고, 숫자가 0개 이상이고, 영문자가 0개 이상인 단어
    words = re.findall(r'\b[A-Za-z]{2,}[A-Za-z0-9]*[A-Za-z]*\b', content)
    
    # Remove stopwords
    words = remove_stop_words(words)
    
    # Remove duplicates
    words = list(set(words))

    # Save words to a txt file
    with open(output_txt_file_path, 'w', encoding='utf-8') as file:
        for word in words:
            file.write(word + '\n')
    
    # Return output txt file path
    return output_txt_file_path

# Usage
directory = 'C:/Users/khy/Documents/workspace/dev_docs/ko/sdk/hive-adiz.html'
# directory = 'C:/Users/khy/Documents/workspace/dev_docs/ko/dev4/ad-monetization/hive-adiz'

def main():
    extract_english_words(directory)
    
if __name__ == '__main__':
    main()