import os
import re

# Function to modify the case style of the heading tags in the HTML file
def modify_heading_tags(html_file, case_style, output_dir):
    with open(html_file, "r", encoding='utf-8') as file:
        html_content = file.read()

    # Define the regex pattern for matching heading tags
    heading_pattern = r"<(h\d.*?)>(.*?)<\/(h\d)>"

    # Define the function to modify the case style of the heading text
    def modify_heading_text(text):
        if case_style == "title":
            return text.title()
        elif case_style == "sentence":
            return text.capitalize()
        else:
            return text

    # Find all heading tags in the HTML content and modify their text
    modified_html = re.sub(heading_pattern, lambda match: f"<{match.group(1)}>{modify_heading_text(match.group(2))}</{match.group(3)}>", html_content)

    # Save the modified HTML file
    output_file = os.path.join(output_dir, "pre-requisites-app-files.html")
    with open(output_file, "w", encoding='utf-8') as file:
        file.write(modified_html)

# Main code
html_file = "C:/Users/khy/Documents/workspace/dev_docs/en/develop/crossplay-launcher/pre-requisites-app-files.html"
output_dir = "C:/Users/khy/Documents/workspace/dev_docs/en/develop/crossplay-launcher/"
case_style = "sentence"

modify_heading_tags(html_file, case_style, output_dir)