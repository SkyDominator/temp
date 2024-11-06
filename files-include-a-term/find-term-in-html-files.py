import os

matched_directories = []

def search(root, file, term):
    if file.endswith(".html"):
        file_path = os.path.join(root, file)
        # file_path = folder + '/' + file
        with open(file_path, "r", encoding='UTF-8') as f:
            content = f.read()
            if term.lower() in content.lower():
                matched_directories.append(file_path)

def search_html_files(folder, term, excluded_directories):
    for root, dirs, files in os.walk(folder):
        _root = root.replace("\\", "/")
        if _root in excluded_directories or any(is_subdirectory(_root, directory) for directory in excluded_directories):
            print("Excluded: " + root)
            continue
        else:
            for file in files:
                search(root, file, term)

def is_subdirectory(directory, parent_directory):
    directory = os.path.abspath(directory)
    parent_directory = os.path.abspath(parent_directory)
    return directory.startswith(parent_directory)    
           
# Example usage
root_folder = "C:/Users/khy/Documents/workspace/DevGuide/ko"
term = "facebook"
excluded_directories = ["C:/Users/khy/Documents/workspace/DevGuide/ko/sdk/archives",
                        "C:/Users/khy/Documents/workspace/DevGuide/ko/sdk/module",
                        "C:/Users/khy/Documents/workspace/DevGuide/ko/sdk/v1",
                        "C:/Users/khy/Documents/workspace/DevGuide/ko/authv1",
                        "C:/Users/khy/Documents/workspace/DevGuide/ko/c2s",
                        "C:/Users/khy/Documents/workspace/DevGuide/ko/hidden",
                        "C:/Users/khy/Documents/workspace/DevGuide/ko/operation",
                        "C:/Users/khy/Documents/workspace/DevGuide/ko/support",
                        "C:/Users/khy/Documents/workspace/DevGuide/ko/v1",
                        "C:/Users/khy/Documents/workspace/DevGuide/en/authv1",
                        "C:/Users/khy/Documents/workspace/DevGuide/en/hidden",
                        "C:/Users/khy/Documents/workspace/DevGuide/en/operation",
                        "C:/Users/khy/Documents/workspace/DevGuide/en/support",
                        ]

search_html_files(root_folder, term, excluded_directories)

for i in range(len(matched_directories)):
    matched_directories[i] = matched_directories[i].replace("C:/Users/khy/Documents/workspace/DevGuide", "https://developers.withhive.com")
    matched_directories[i] = matched_directories[i].replace(".html", "")
    
# Save the result to a text file
with open("matched_webpages.txt", "w", encoding='UTF-8') as f:
    for page in matched_directories:
        f.write(page + "\n")

print("Result saved to matched_webpages.txt")




