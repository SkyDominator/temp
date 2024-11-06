import re
import json
from collections import defaultdict

# Define the file path
file_path = 'C:/Users/khy/Documents/workspace/concordance_search/2023-12-30-HiveSDK-KO-EN.tmx'

# Read the file content
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Regular expression to match each translation unit (tu)
tu_pattern = r'<tu creationdate="([^"]+)" .*?changedate="([^"]+)"[^>]*>(.*?)<\/tu>'

# Find all translation units in the content
tu_matches = re.findall(tu_pattern, content, re.DOTALL)

# Test code
# print(len(tu_matches))
# print('gg')

# Filter matches to ensure they contain both Korean and English segments
filtered_final_matches = [m for m in tu_matches if '<tuv xml:lang="KO">' in m[2] and '<tuv xml:lang="EN">' in m[2]]

# Create a dictionary to store the filtered and refined records
final_full_records = {}

# set counter
counter = 0

# Process each filtered match and add it to the dictionary
for (creationdate, changedate, content) in filtered_final_matches:
    # Extract the Korean and English segments from the content
    # <tuv xml:lang="KO">
    # <tuv xml:lang="EN">
    korean_match = re.search(r'<tuv xml:lang="KO">\n\s+<seg>(.*?)<\/seg>', content, re.DOTALL)
    english_match = re.search(r'<tuv xml:lang="EN">\n\s+<seg>(.*?)<\/seg>', content, re.DOTALL)
    
    if korean_match and english_match:
        
        korean = korean_match.group(1).strip()
        english = english_match.group(1).strip()
        key = counter
        final_full_records[key] = {'Korean': korean, 'English': english, 'CreationDate': creationdate, 'ChangeDate': changedate}
        counter+=1

# Define the path to save the parsed records
output_file_path = 'C:/Users/khy/Documents/workspace/concordance_search/data/full_parsed_records.json'

# Save the records to a JSON file
with open(output_file_path, 'w', encoding='utf-8') as outfile:
    json.dump(final_full_records, outfile, ensure_ascii=False, indent=4)
