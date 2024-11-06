from collections import defaultdict
import json
import re

output_file_path = 'C:/Users/khy/Documents/workspace/concordance_search/data/full_parsed_records.json'

# Load the previously parsed translation records
with open(output_file_path, 'r', encoding='utf-8') as infile:
    translation_records = json.load(infile)

# Create default dictionaries for the inverted indexes
korean_inverted_index = defaultdict(set)
english_inverted_index = defaultdict(set)

# Populate the inverted indexes
for key, record in translation_records.items():
    # Tokenize the Korean and English segments (naively using spaces and common punctuation)
    korean_tokens = re.split(r'\s+|,|\.|\(|\)|\[|\]|\'|"|;|:|!', record['Korean'])
    english_tokens = re.split(r'\s+|,|\.|\(|\)|\[|\]|\'|"|;|:|!', record['English'])

    for token in korean_tokens:
        if token:  # ensuring no empty strings are added
            korean_inverted_index[token].add(key)
    for token in english_tokens:
        if token:
            english_inverted_index[token].add(key)

# Convert the sets in the inverted index to lists for JSON serialization
korean_inverted_index = {word: list(keys) for word, keys in korean_inverted_index.items()}
english_inverted_index = {word: list(keys) for word, keys in english_inverted_index.items()}

# Define paths to save the inverted indexes
korean_index_path = 'C:/Users/khy/Documents/workspace/concordance_search/data/korean_inverted_index.json'
english_index_path = 'C:/Users/khy/Documents/workspace/concordance_search/data/english_inverted_index.json'

# Save the inverted indexes to JSON files
with open(korean_index_path, 'w', encoding='utf-8') as outfile:
    json.dump(korean_inverted_index, outfile, ensure_ascii=False, indent=4)
with open(english_index_path, 'w', encoding='utf-8') as outfile:
    json.dump(english_inverted_index, outfile, ensure_ascii=False, indent=4)

korean_index_path, english_index_path
