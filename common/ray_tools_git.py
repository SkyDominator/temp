import git
import os, sys
from typing import List, Dict
import requests
from dotenv import load_dotenv

load_dotenv(os.path.normpath(r'C:\Users\raykim\Documents\workspace\personal\workspace\toolbox\common\env\data.env'))
GITLAB_PROJECT_TOKEN = os.getenv('GITLAB_PROJECT_TOKEN')
GITLAB_API_URL = "https://xgit.withhive.com/api/v4"
GITLAB_PROJECT_ID = "1072"

# Initialize the repo
REPO_PATH = os.path.normpath(r"C:\Users\raykim\Documents\workspace\devsite_mk")
REPO = git.Repo(REPO_PATH)

headers = {
    "PRIVATE-TOKEN": GITLAB_PROJECT_TOKEN
}

def get_first_commit_after_checkout(repo: git.Repo, master: str, feature: str) -> str:
    # Get the commit where the feature branch was created from the master branch
    merge_base = repo.merge_base(master, feature)[0]
    
    # Get the first commit on the feature branch after it diverged from the master branch
    commits = list(repo.iter_commits(f'{merge_base.hexsha}..{feature}'))
    if commits:
        first_commit = commits[-1]
        return first_commit.hexsha
    else:
        return None

def get_files_changed_in_commits(commit_hashes: List[str]) -> List[str]:
    changed_files = set()
    for commit_hash in commit_hashes:
        commit = REPO.commit(commit_hash)
        for parent in commit.parents:
            diff = REPO.git.diff(parent.hexsha, commit.hexsha, name_only=True)
            changed_files.update(diff.split('\n'))
    return list(changed_files)

def compare_master_feature(master, feature):
    first_commit_hash = get_first_commit_after_checkout(REPO, master, feature)
    if (first_commit_hash):
        print(f"The first commit hash on the feature branch after checkout from master is: {first_commit_hash}")
    else:
        print("No commits found on the feature branch after it diverged from the master branch.")
        
    # Get the last commit hash on the feature branch
    last_commit_hash = REPO.commit(feature).hexsha
    
    # Compare the first commit hash and the last commit hash
    if first_commit_hash and last_commit_hash:
        # Get the list of files changed between the first and last commit on the feature branch
        diff = REPO.git.diff(f'{first_commit_hash}..{last_commit_hash}', name_only=True)
        changed_files = diff.split('\n')
        
        print(f"Files changed between {first_commit_hash} and {last_commit_hash}:")
        return changed_files
    else:
        print("Could not determine the commit range for the feature branch.")

def get_gitlab_mr_changes(mr_id: int) -> List[str]:
    url = f"{GITLAB_API_URL}/projects/{GITLAB_PROJECT_ID}/merge_requests/{mr_id}/changes"
    headers = {
        "PRIVATE-TOKEN": GITLAB_PROJECT_TOKEN
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        changes = response.json().get('changes', [])
        changed_files = [change['new_path'] for change in changes]
        return changed_files
    else:
        print(f"Failed to fetch changes for MR {mr_id}. Status code: {response.status_code}")
        return []


def get_mr_commits(mr_id: int) -> List[Dict]:
    url = f"{GITLAB_API_URL}/projects/{GITLAB_PROJECT_ID}/merge_requests/{mr_id}/commits"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        commits = response.json()
        return commits
    else:
        raise Exception(f"Failed to get commits for MR {mr_id}: {response.text}")

def get_prev_commit_sha_on_remote(first_commit_sha: str) -> str:
    url = f"{GITLAB_API_URL}/projects/{GITLAB_PROJECT_ID}/repository/commits/{first_commit_sha}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        commit_info = response.json()
        parent_ids = commit_info.get('parent_ids', [])
        if parent_ids:
            return parent_ids[0]
        else:
            raise Exception("First commit has no parent commit.")
    else:
        raise Exception(f"Failed to get commit info for {first_commit_sha}: {response.text}")

def get_prev_commit_sha_on_remote(first_commit_sha: str) -> str:
    url = f"{GITLAB_API_URL}/projects/{GITLAB_PROJECT_ID}/repository/commits/{first_commit_sha}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        commit_info = response.json()
        parent_ids = commit_info.get('parent_ids', [])
        if parent_ids:
            return parent_ids[0]
        else:
            raise Exception("First commit has no parent commit.")
    else:
        raise Exception(f"Failed to get commit info for {first_commit_sha}: {response.text}")

def get_file_content_at_commit_on_remote(file_path: str, commit_sha: str) -> str:
    encoded_path = requests.utils.quote(file_path, safe='')
    url = f"{GITLAB_API_URL}/projects/{GITLAB_PROJECT_ID}/repository/files/{encoded_path}/raw?ref={commit_sha}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        # If file does not exist at this commit, return empty
        if response.status_code == 404:
            return ''
        else:
            raise Exception(f"Failed to get file content: {response.text}")
        
def get_diff_commits_between_branches(branch1: str, branch2: str) -> List[str]:
    # Get the list of commits in branch1 that are not in branch2, excluding merge commits
    branch1_commits = [commit for commit in REPO.iter_commits(branch1)]
    branch2_commits = set(commit.hexsha for commit in REPO.iter_commits(branch2))
    
    diff_commits = [commit.hexsha for commit in branch1_commits if commit.hexsha not in branch2_commits]
    
    # Return commits in chronological order (oldest first)
    diff_commits.reverse()
    return diff_commits

def get_diff_commits_between_branches_without_merge_commits(branch1: str, branch2: str) -> List[str]:
    # Get the list of commits in branch1 that are not in branch2, excluding merge commits
    branch1_commits = [commit for commit in REPO.iter_commits(branch1) if len(commit.parents) == 1]
    branch2_commits = set(commit.hexsha for commit in REPO.iter_commits(branch2) if len(commit.parents) == 1)
    
    diff_commits = [commit.hexsha for commit in branch1_commits if commit.hexsha not in branch2_commits]
    
    # Return commits in chronological order (oldest first)
    diff_commits.reverse()
    return diff_commits

def get_commits_affecting_file(file_path: str, commit_hashes: List[str]) -> List[str]:
    affecting_commits = []
    for commit_hash in commit_hashes:
        commit = REPO.commit(commit_hash)
        if file_path in commit.stats.files:
            affecting_commits.append(commit_hash)
    return affecting_commits

def get_previous_commit(commit_sha: str) -> str:
    commit = REPO.commit(commit_sha)
    if commit.parents:
        return commit.parents[0].hexsha
    else:
        raise Exception(f"Commit {commit_sha} has no parent commit.")

def get_file_content_at_commit(file_path: str, commit_sha: str) -> str:
    commit = REPO.commit(commit_sha)
    blob = commit.tree / file_path
    return blob.data_stream.read().decode('utf-8')

def is_file_changed_on_commit(file_path: str, commit_sha: str) -> str:
    commit = REPO.commit(commit_sha)
    parent = commit.parents[0] if commit.parents else None
    if parent:
        diffs = parent.diff(commit)
        for diff in diffs:
            if diff.a_path == file_path or diff.b_path == file_path:
                return True
        return False
    else:
        return False
    
def get_file_before_commits(file_path: str, commit_hashes: List[str]) -> str:
    if not commit_hashes:
        return ''
    
    # Get the content of the file at the commit before the first commit in the list
    first_commit = commit_hashes[0]
    prev_commit = get_previous_commit(first_commit)
    file_content = get_file_content_at_commit(file_path, prev_commit)
    
    return file_content

def get_file_after_commits(file_path: str, commit_hashes: List[str]) -> str:
    if not commit_hashes:
        return ''
    
    # Get the content of the file at the last commit in the list
    last_commit = commit_hashes[-1]
    file_content = get_file_content_at_commit(file_path, last_commit)
        
    return file_content



