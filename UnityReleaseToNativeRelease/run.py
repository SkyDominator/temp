import re

def find_replace_html(file_path, regex_patterns, regex_patterns_empty):
    # Read the HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Apply regex patterns sequentially
    for pattern, replacement in regex_patterns:
        html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    
    # Remove empty list pattern
    html_content = re.sub(regex_patterns_empty[0], regex_patterns_empty[1], html_content)
    
    # Save the modified HTML file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

# # Example usage - KO
file_path_and = 'C:/Users/khy/Documents/workspace/DevGuide/ko/sdk/v4-ks/android.html'
file_path_ios = 'C:/Users/khy/Documents/workspace/DevGuide/ko/sdk/v4-ks/ios.html'

# Example usage - EN
# file_path_and = 'C:/Users/khy/Documents/workspace/DevGuide/en/sdk/v4-ks/android.html'
# file_path_ios = 'C:/Users/khy/Documents/workspace/DevGuide/en/sdk/v4-ks/ios.html'

# iOS 패턴
regex_patterns_ios = [
    (r'<h6>Unity<\/h6>\n\[su_spacer size="10"\]\n<ul.*?>\n(.*?\n)+?<\/ul>', ''),
    (r'<ul style=\"list-style-type: none;\">', '<ul>'),
    (r'<li><span class=\"targetLabel android\">Android<\/span>\s.*?<\/li>', ''),
    (r'<li><span class=\"targetLabel iOS\">iOS<\/span>\s(.*?)<\/li>', r'<li>\1</li>'),
    (r'<li><span class=\"targetLabel common\">All<\/span>\s(.*?)<\/li>', r'<li>\1</li>'),
    # Add more regex patterns as needed
]

# Android 패턴
regex_patterns_and = [
    (r'<h6>Unity<\/h6>\n\[su_spacer size="10"\]\n<ul.*?>\n(.*?\n)+?<\/ul>', ''),
    (r'<ul style=\"list-style-type: none;\">', '<ul>'),
    (r'<li><span class=\"targetLabel iOS\">iOS<\/span>\s.*?<\/li>', ''),
    (r'<li><span class=\"targetLabel android\">Android<\/span>\s(.*?)<\/li>', r'<li>\1</li>'),
    (r'<li><span class=\"targetLabel common\">All<\/span>\s(.*?)<\/li>', r'<li>\1</li>'),
    # Add more regex patterns as needed
]

regex_patterns_empty = (r'<h6>.*?<\/h6>\n\[su_spacer size="10"\]\n<ul.*?>\s+?<\/ul>', '')

find_replace_html(file_path_and, regex_patterns_and, regex_patterns_empty)
find_replace_html(file_path_ios, regex_patterns_ios, regex_patterns_empty)

#TODO: \n\s+\n을 찾아서 제거하는 로직 추가