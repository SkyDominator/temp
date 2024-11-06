from bs4 import BeautifulSoup, NavigableString
import html
import re
from decorators import process_file_or_files_in_dir

@process_file_or_files_in_dir
def wrap_words_with_span(ko_html_file_path):
    # Set input and output file paths
    txt_file_path = re.sub(r'\.html', '_TR_SKIPS.txt', ko_html_file_path)
    html_file_path = re.sub(r'\/ko\/dev4', '/en/develop', ko_html_file_path)
    html_file_path = re.sub(r'\/ko\/', '/en/', html_file_path)
    output_html_file_path = html_file_path

    # Read words from the txt file
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        words = [line.strip() for line in file.readlines()]

    # Read the HTML content
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # ============================================================
    # Pre-process
    # Replace `` with <code>...</code>
    html_content = re.sub(r'`(.*?)`', r'<code>\1</code>', html_content, flags=re.DOTALL)
    
    # Replace matched strings with exclude_patterns with placeholders in html_content
    # Must be out-of-HTML-tag-area texts
    # The order of the patterns in the list is important!!
    exclude_patterns_for_string = [
        r"\[av_tab_container.*?\[\/av_tab_container\]",
        r'\[\/?su_.*?\]', # Inside a WordPress shortcode
        r'\[\/?av_.*?\]', # Inside a WordPress shortcode
        r'\[\/?caption.*?\]', # Inside a WordPress shortcode
        r'<pre.*?>.*?<\/pre>', # all contents inside the a pre tag
        r'<code.*?>.*?<\/code>', # all contesnts inside the a code tag
        r'&nbsp;', # &nbsp;
        ]

    placeholders = {} 
    counter = 0  # Counter to ensure unique placeholders
    
    def replace_with_placeholder(regex, content, wrap=False):
        def replacer(match):
            nonlocal counter
            placeholder = f"[PLACEHOLDER_{counter}]"
            placeholders[placeholder] = (match.group(0), wrap)
            counter += 1
            return placeholder
        return re.sub(regex, replacer, content, flags=re.DOTALL)
    
    for i in range(len(exclude_patterns_for_string)):
        pattern = exclude_patterns_for_string[i]
        if i == 0:
            html_content = replace_with_placeholder(pattern, html_content, wrap=True)
        else:
            html_content = replace_with_placeholder(pattern, html_content)
    
    # Function to remove <div class="notranslate"></div> 
    html_content = re.sub(r'<div class="notranslate">(.*?)</div>', r'\1', html_content, flags=re.DOTALL)
    # Function to remove <span class="notranslate"></span>
    span_pattern = re.compile(r'<span class="notranslate">(.*?)</span>', flags=re.DOTALL)
    while re.search(span_pattern, html_content):
        html_content = re.sub(span_pattern, r'\1', html_content)
    
    # remove "notranslate" class attributes from all HTML tags
    html_content = re.sub(r'(<[^>]*?)\sclass="[^"]*?notranslate[^"]*?"', r'\1', html_content)
    
    # ============================================================
    # Load soup, define functions to process text nodes, and wrap words            
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # ============================================================
    # Combine exclude_patterns into a single pattern
    # Except for HTML tags (HTML tags are processed separately in the next step)
    exclude_patterns_for_soup = [
        r'\[PLACEHOLDER_\d*?\]', # Inside a code line
        ]
    entire_patterns = [
        r'http[s]?://\S+',
        r'[a-zA-Z0-9]+(?:[!@#$%^*_+=:.?\-]{1}[a-zA-Z0-9]+){2,}', #build.gradle과 같은 영-특-영 패턴은 잡아내지 못하므로 직접 수동으로 처리해야 함.
    ]
    
    combined_pattern = '|'.join('{}'.format(pattern) for pattern in exclude_patterns_for_soup + entire_patterns)
    
    # Function to find and wrap words
    def wrap_word(text):
        for word in words:
            text = re.sub(r'\b{}\b'.format(re.escape(word)), r'<span class="notranslate">\g<0></span>', text)
        return text
    
    # Function to wrap text node based on specific regex pattern
    def wrap_text_node(text_node):
        # Split the text_node by the combined_exclude_pattern and include the pattern in the result
        parts = re.split('({})'.format(combined_pattern), text_node)
        processed_text = ''

        for part in parts:
            # If part matches any of the entire_patterns, wrap the entire part
            if any(re.fullmatch(entire_pattern, part) for entire_pattern in entire_patterns):
                processed_text += f'<span class="notranslate">{part}</span>'
            # If part matches any of the exclude_patterns, keep it as it is
            elif any(re.fullmatch(exclude_pattern, part) for exclude_pattern in exclude_patterns_for_soup):
                processed_text += part
            # If not, apply wrap_text_in_text_nodes to this part
            else:
                processed_text += wrap_word(part)
        return processed_text
    
    # Exclude specific areas and wrap words
    for text_node in soup.find_all(string=True):
        if isinstance(text_node, NavigableString):
            # Check the entire hierarchy for excluded tags
            skip = False
            for parent in text_node.parents:
                if parent.name in ['table', 'em', 'b', 'strong']:
                    skip = True
                    break
            
            if skip == False:
                try:
                    wrapped_text = wrap_text_node(text_node)
                    text_node.replace_with(wrapped_text)
                except Exception as e:
                    print(e)
                    # text_node.wrap(soup.new_tag('span', **{'class': 'notranslate'})) # What a beautiful code!
    
    # ============================================================
    # Process HTML tags: <em>, <table>, <b>, <strong>
    # Replace and store <em> content with placeholders
    for em_tag in soup.find_all('em'):
        # Wrap the whole <em> tag area 
        em_tag.replace_with(f'<span class="notranslate">{em_tag}</span>')

    # Replace and store <b> content with placeholders
    for b_tag in soup.find_all('b'):
        # Wrap the whole <b> tag area 
        b_tag.replace_with(f'<span class="notranslate">{b_tag}</span>')

    # Replace and store <strong> content with placeholders
    for strong_tag in soup.find_all('strong'):
        # Wrap the whole <strong> tag area 
        strong_tag.replace_with(f'<span class="notranslate">{strong_tag}</span>')
        
    # Add 'notranslate' class to tables
    for table in soup.find_all('table'):
        existing_classes = table.get('class', [])
        if existing_classes is None:
            table['class'] = ['notranslate']
        else:
            table['class'] = existing_classes + ['notranslate']
        
    # ============================================================
    # Convert soup back to string
    modified_html = str(soup)
   
    # Restore placeholders, wrapping content if necessary
    for placeholder, (original, wrap) in placeholders.items():
        # wrapped = f'<span class="notranslate">{original}</span>' if wrap else original
        wrapped = f'<div class="notranslate">{original}</div>' if wrap else original
        modified_html = modified_html.replace(placeholder, wrapped)
    
    # &lt; &gt; &amp; &quot; &apos; to < > & " '
    def fully_unescape(html_content):
        # Define a pattern to match any HTML escaped character except &nbsp; (non-breaking space)
        escaped_char_pattern = re.compile(r'&(?!nbsp;)[#\w]+;')        
        # Continue unescaping until there are no more escapable characters
        while escaped_char_pattern.search(html_content):
            # html_content = html.unescape(html_content)
            html_content = re.sub(escaped_char_pattern, lambda m: html.unescape(m.group(0)), html_content)
        return html_content
    
    modified_html = fully_unescape(modified_html)
    
    # Save the modified HTML content
    with open(output_html_file_path, 'w', encoding='utf-8') as file:
        file.write(modified_html)

# Usage
html_file_path = 'C:/Users/khy/Documents/workspace/dev_docs/ko/dev4/hercules/getting-started.html'

def main():
    wrap_words_with_span(html_file_path)
    
if __name__ == '__main__':
    main()
