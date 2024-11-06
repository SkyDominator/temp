import os, sys
import regex as re
from functools import wraps
# from markdownify import markdownify as md
from markdownify import MarkdownConverter

# Add the path to your custom module
sys.path.append(os.path.abspath('C:/Users/raykim/Documents/workspace/personal/workspace/toolbox/common'))
import ray_tools  # Import your custom module

# Rest of your code...

AV_TITLE_DICT = {'unity®': 'cs',
                 'c++': 'cpp',
                 'kotlin': 'kt',
                 'java': 'java',
                 'swift': 'swift',
                 'obj-c': 'objc',
                 'objective-c': 'objc',
                 'ios': 'objc',
                 'android': 'java',}

AV_TITLE_REV_DICT = {
                 'cs':'Unity',
                 'cpp': 'C++',
                 'kt': 'Kotlin',
                 'java': 'Java',
                 'swift': 'Swift',
                 'objc': 'Objective-C',}
CGV_DICT = {
        '[cgv hive_sdk4_unity_api_ref]':'http://developers.withhive.com/HTML/v4_api_reference/Unity3D',
    '[cgv hive_sdk4_unity_api_ref_en]':'http://developers.withhive.com/HTML/v4_api_reference_en/Unity3D',
        '[cgv hive_sdk4_cpp_api_ref]':'http://developers.withhive.com/HTML/v4_api_reference/CPP',
    '[cgv hive_sdk4_cpp_api_ref_en]':'http://developers.withhive.com/HTML/v4_api_reference_en/CPP',
        '[cgv hive_sdk4_android_api_ref]':'http://developers.withhive.com/HTML/v4_api_reference/Android',
    '[cgv hive_sdk4_android_api_ref_en]':'http://developers.withhive.com/HTML/v4_api_reference_en/Android',
    '[cgv hive_sdk4_ios_api_ref]':'http://developers.withhive.com/HTML/v4_api_reference/iOS',
    '[cgv hive_sdk4_ios_api_ref_en]':'http://developers.withhive.com/HTML/v4_api_reference_en/iOS',
            }

def indent_code_blocks(match):
    # Indent the code block by four spaces
    lang_name = match.group(1)
    input_string = re.sub(r'\n', '\n    ', match.group(2))
    input_string = re.sub(r'(.*?)(?=\n)', r'    \1', input_string)
    # re.sub 결과로 리턴하는 string은 왜 raw string이면 안 되는 건가? raw string으로 하면 \n을 escape하지 못하고 문자 그대로 반환함.
    return f'    ```{lang_name}\n{input_string}\n    ```'

# def remove_extra_newlines(match):
#     # Replace multiple new line characters with a single new line character
#     input_string = re.sub(r'\n+', '\n', match.group(0))
    
#     # Replace multiple carriage return characters with a single carriage return character
#     input_string = re.sub(r'\r+', '\r', input_string)
    
#     return input_string

def strip_citation_marks(input_string):
    # List of citation marks to remove
    citation_marks = ['"', "'", "`"]

    # Remove citation marks from the input string
    for mark in citation_marks:
        input_string = input_string.replace(mark, '')

    return input_string

def parse_link(link):
    for key, value in CGV_DICT.items():
        if key in link:
            return link.replace(key, value)
    raise ValueError(f'Invalid link: {link}')

def to_mkdocs_code_tabs_with_api_refs(match):
    title = strip_citation_marks(match.group('TITLE_NAME'))
    codes = match.group('CODES').strip()
    lang_name = AV_TITLE_DICT.get(title.lower())
    new_title = AV_TITLE_REV_DICT.get(lang_name)
    api_ref_link = match.group('API_REF_LINK')
    
    if api_ref_link.startswith('[cgv'):
        api_ref_link = parse_link(api_ref_link)
    replace = f'=== "{new_title}"\n    API Reference: [{match.group("API_REF_NAME")}]({api_ref_link})\n\n```{lang_name} linenums="1"\n{codes}\n```\n'

    return replace

def to_mkdocs_code_tabs(match):
    title = strip_citation_marks(match.group('TITLE_NAME'))
    codes = match.group('CODES').strip()
    lang_name = AV_TITLE_DICT.get(title.lower())
    new_title = AV_TITLE_REV_DICT.get(lang_name)
    replace = f'=== "{new_title}"\n\n```{lang_name} linenums="1"\n{codes}\n```'

    return replace


def read_html_file_from_input():
    # Read the HTML file from text keyboard input
    html = input("Enter the HTML content: ")
    return html

class CustomConverter(MarkdownConverter):
    '''
    test
    '''
    ATX = 'atx'
    ATX_CLOSED = 'atx_closed'
    UNDERLINED = 'underlined'
    SETEXT = UNDERLINED
    
    def convert_hn(self, n, el, text, convert_as_inline):
        if convert_as_inline:
            return text

        style = self.options['heading_style'].lower()
        text = text.rstrip()
        if style == CustomConverter.UNDERLINED and n <= 2:
            line = '=' if n == 1 else '-'
            return self.underline(text, line)
        hashes = '#' * n
        if style == CustomConverter.ATX_CLOSED:
            return '%s %s %s\n\n' % (hashes, text, hashes)
        
        id = el.get('id')
        if id == None:
            return '%s %s\n\n' % (hashes, text)
        else:
            return '%s %s { #%s }\n\n' % (hashes, text, id)
    
    def convert_img(self, el, text, convert_as_inline):
        alt = el.attrs.get('alt', None) or ''
        src = el.attrs.get('src', None) or ''
        title = el.attrs.get('title', None) or ''
        width = el.attrs.get('width', None) or ''
        if "px" not in width:
            width = width + "px"
        
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        if (convert_as_inline
                and el.parent.name not in self.options['keep_inline_images_in']):
            return alt

        return '![%s](%s%s){width="%s"}' % (alt, src, title_part, width)
    
    def convert_nbsp(self, el, text, convert_as_inline):
        # Replace &nbsp; with a regular space
        return '<br>'
    
    def convert_em(self, el, text, convert_as_inline):
        def chomp(text):
            """
            If the text in an inline tag like b, a, or em contains a leading or trailing
            space, strip the string and return a space as suffix of prefix, if needed.
            This function is used to prevent conversions like
                <b> foo</b> => ** foo**
            """
            prefix = ' ' if text and text[0] == ' ' else ''
            suffix = ' ' if text and text[-1] == ' ' else ''
            text = text.strip()
            return (prefix, suffix, text)
    
        markup_start = "<i>" 
        markup_end = "</i>" 
        prefix, suffix, text = chomp(text)
        if not text:
            return ''
        return '%s%s%s%s%s' % (prefix, markup_start, text, markup_end, suffix)
    
    convert_i = convert_em
    
    def convert_b(self, el, text, convert_as_inline):
        def chomp(text):
            """
            If the text in an inline tag like b, a, or em contains a leading or trailing
            space, strip the string and return a space as suffix of prefix, if needed.
            This function is used to prevent conversions like
                <b> foo</b> => ** foo**
            """
            prefix = ' ' if text and text[0] == ' ' else ''
            suffix = ' ' if text and text[-1] == ' ' else ''
            text = text.strip()
            return (prefix, suffix, text)
    
        markup_start = "<b>" 
        markup_end = "</b>" 
        prefix, suffix, text = chomp(text)
        if not text:
            return ''
        return '%s%s%s%s%s' % (prefix, markup_start, text, markup_end, suffix)
    
    convert_strong = convert_b
    
    def convert_br(self, el, text, convert_as_inline):
        return '<br>'
    
    def convert_ul(self, el, text, convert_as_inline):
        if el.find_parent('table'):
            return str(el)
        return self.convert_list(el, text, convert_as_inline)

    def convert_ol(self, el, text, convert_as_inline):
        if el.find_parent('table'):
            return str(el)
        return self.convert_list(el, text, convert_as_inline)

    def convert_list(self, el, text, convert_as_inline):
        # Converting a list to inline is undefined.
        # Ignoring convert_to_inline for list.

        nested = False
        before_paragraph = False
        if el.next_sibling and el.next_sibling.name not in ['ul', 'ol']:
            before_paragraph = True
        while el:
            if el.name == 'li':
                nested = True
                break
            el = el.parent
        if nested:
            # remove trailing newline if nested
            return '\n' + self.indent(text, 1).rstrip()
        return text + ('\n' if before_paragraph else '')
    
    def convert_table(self, el, text, convert_as_inline):
        return '\n\n' + text + '\n'

    def convert_td(self, el, text, convert_as_inline):
        return ' ' + text + ' |'

    def convert_th(self, el, text, convert_as_inline):
        return ' ' + text + ' |'

    def convert_tr(self, el, text, convert_as_inline):
        cells = el.find_all(['td', 'th'])
        is_headrow = all([cell.name == 'th' for cell in cells])
        overline = ''
        underline = ''
        if is_headrow and not el.previous_sibling:
            # first row and is headline: print headline underline
            underline += '| ' + ' | '.join(['---'] * len(cells)) + ' |' + '\n'
        elif (not el.previous_sibling
              and (el.parent.name == 'table'
                   or (el.parent.name == 'tbody'
                       and not el.parent.previous_sibling))):
            # first row, not headline, and:
            # - the parent is table or
            # - the parent is tbody at the beginning of a table.
            # print empty headline above this row
            overline += '| ' + ' | '.join([''] * len(cells)) + ' |' + '\n'
            overline += '| ' + ' | '.join(['---'] * len(cells)) + ' |' + '\n'
        return overline + '|' + text + '\n' + underline
    
def md(html, **options):
    return CustomConverter(**options).convert(html)
    
    
def backup_pattern(html, pattern, placeholder_string):
    # Find the code snippet contents block within [av_tab_container] shortcode
    backups = re.findall(pattern, html, re.DOTALL)
    
    # Replace code snippets from the WordPress HTML file
    converted_html = html
    counter = 0
    for backup in backups:
        converted_html = converted_html.replace(backup, '[[[{placeholder_string}{counter}]]]'.format(placeholder_string=placeholder_string, counter=counter))
        counter += 1
    return converted_html, backups

def backup_tables(html, placeholder_string="TABLESNIPPET"):
    pattern = r'<table.*?>.*?<\/table>'
    tables = re.findall(pattern, html, re.DOTALL)
    backups = []
    converted_html = html

    for table in tables:
        if 'rowspan' in table or 'colspan' in table or '<aside' in table:
            placeholder = '[[[{placeholder_string}{counter}]]]'.format(placeholder_string=placeholder_string, counter=len(backups))
            converted_html = converted_html.replace(table, placeholder)
            backups.append(table)
        else:
            continue

    return converted_html, backups

def restore_backups(markdown, backups, placeholder_string):
    # Restore code snippets to the input string
    for counter, backup in enumerate(backups):
        markdown = markdown.replace('[[[{placeholder_string}{counter}]]]'.format(placeholder_string=placeholder_string, counter=counter), backup)
    return markdown

def convert(wordpress_html):
    wordpress_html = wordpress_html.replace("\n\n&nbsp;\n\n", "\n<br>\n\n")
    wordpress_html = wordpress_html.replace("&nbsp;", "\n<br>\n")

    ### 
    pattern = r'\[av_tab_container.*?\].*?\[\/av_tab_container\]'
    # ph_string에는 esacpe 처리하는 문자열을 넣으면 안 됨 
    code_ph_string = "CODESNIPPET"
    converted_html, code_snippets = backup_pattern(wordpress_html, pattern, code_ph_string)

    ### 
    pattern = r'\[markdown.*?\].*?\[\/markdown\]'
    markdown_ph_string = "MARKDOWNSNIPPET"

    converted_html, markdown_snippets = backup_pattern(converted_html, pattern, markdown_ph_string)
    
    ###
    pattern = r'<aside class=(?:"|\')note(?:"|\')>'
    note_opening_ph_string = "NOTEOPENINGSNIPPET"

    converted_html, note_opening_snippets = backup_pattern(converted_html, pattern, note_opening_ph_string)
    converted_html = converted_html.replace("</aside>", "")

    ###
    pattern = r'<aside class=(?:"|\')important(?:"|\')>'
    important_opening_ph_string = "IMPORTANTOPENINGSNIPPET"

    converted_html, important_opening_snippets = backup_pattern(converted_html, pattern, important_opening_ph_string)
    converted_html = converted_html.replace("</aside>", "")

    ###
    table_ph_string = "TABLESNIPPET"
    converted_html, table_snippets = backup_tables(converted_html, table_ph_string)

    ### 
    markdown = md(converted_html, heading_style="ATX", newline_style="BACKSLASH")

    ###
    # converted_markdown = re.sub(r'(\n\s)+', '\n\n', markdown)

    ###
    converted_markdown = restore_backups(markdown, code_snippets, code_ph_string)
    
    ###
    converted_markdown = restore_backups(converted_markdown, markdown_snippets, markdown_ph_string)
    # Remove "[markdown]" and "[/markdown]" strings from converted_html
    converted_markdown = converted_markdown.replace("[markdown]", "").replace("[/markdown]", "")

    ###
    converted_markdown = restore_backups(converted_markdown, note_opening_snippets, note_opening_ph_string)

    ###
    converted_markdown = restore_backups(converted_markdown, important_opening_snippets, important_opening_ph_string)

    ###
    converted_markdown = restore_backups(converted_markdown, table_snippets, table_ph_string)

    ###
    # pattern = r'\*\*(?P<bold_text>.*?)\*\*'
    # def replace_bold(match):
    #     return f'<b>{match.group("bold_text")}</b>'
    # converted_markdown = re.sub(pattern, replace_bold, converted_markdown, re.DOTALL)

    # pattern = r'\*(?P<italic_text>.*?)\*'
    # def replace_italic(match):
    #     return f'<i>{match.group("italic_text")}</i>'
    # converted_markdown = re.sub(pattern, replace_italic, converted_markdown, re.DOTALL)

    ###
    pattern = r'<aside class=(?:"|\')note(?:"|\')>'
    converted_markdown = re.sub(pattern, '???+ note\n', converted_markdown, re.DOTALL)
    # pattern = r'<aside class=(?:"|\')note(?:"|\')>\s+?(\S.*?)\s{2}'
    # converted_markdown = re.sub(pattern, r'???+ note\n    \g<1>', converted_markdown, re.DOTALL)

    ###
    pattern = r'<aside class=(?:"|\')important(?:"|\')>'
    converted_markdown = re.sub(pattern, '???+ warning\n', converted_markdown, re.DOTALL)

    ###
    pattern = r'\[av_tab_container.*?\]'
    converted_markdown = re.sub(pattern, '', converted_markdown, re.DOTALL)

    pattern = r'\[\/av_tab_container\]'
    converted_markdown = re.sub(pattern, '', converted_markdown, re.DOTALL)

    ###
    pattern = r'\[av_tab title=(?P<TITLE_NAME>\S+?)(?:\]| .*?\])\n<strong>API Reference<\/strong>.*?<a href="(?P<API_REF_LINK>.*?)".*?>(?P<API_REF_NAME>.*?)<\/a>\n<pre.*?>\s*?(?:<code.*?>)?(?P<CODES>.*?)(?:<\/code>)?\s*?<\/pre>\s*?\[\/av_tab\]'
    converted_markdown = re.sub(pattern, to_mkdocs_code_tabs_with_api_refs, converted_markdown, flags=re.DOTALL)

    ###
    pattern = r'\[av_tab title=(?P<TITLE_NAME>\S+?)(?:\]| .*?\])\n<pre.*?>\s*?(?:<code.*?>)?(?P<CODES>.*?)(?:<\/code>)?\s*?<\/pre>\s*?\[\/av_tab\]'
    converted_markdown = re.sub(pattern, to_mkdocs_code_tabs, converted_markdown, flags=re.DOTALL)

    ###
    # pattern = r'```(.*?)```'
    # converted_markdown = re.sub(pattern, remove_extra_newlines, converted_markdown, flags=re.DOTALL)

    ###
    # pattern = r'```(cs|cpp|kt|java|swift|objc)\n(.*?)\n```'
    pattern = r'```(cs|cpp|kt|java|swift|objc) linenums="1"\n(.*?)\n```'
    converted_markdown = re.sub(pattern, indent_code_blocks, converted_markdown, flags=re.DOTALL)
    
    ###
    converted_markdown = re.sub(r'\n{3,}', '\n\n', converted_markdown)
    
    return converted_markdown

def main():
    # test
    test_html = ray_tools.read_md_file(r'C:\Users\raykim\Documents\workspace\devsite_mk\docs\ko\releases\hive-adkit\adx\cpp.md')
    markdown_output = convert(test_html)
    print(markdown_output)
    
if __name__ == '__main__':
    main()