import requests
import time
import random

# Replace with your GitHub personal access token
GITHUB_TOKEN = ""

# GitHub username
GITHUB_USERNAME = ""

# Set of languages to search for and their required files
LANGUAGES_AND_FILES = {
    "Python": ["requirements.txt"],
    "JavaScript": ["package.json"],
    "Java": ["pom.xml"],
    "Rust": ["Cargo.toml"],
    "Go": ["go.mod"]  # Major package manager file for Go is go.mod
}

# Base GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# Headers for the GitHub API request
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Number of repositories to fork per language
NUM_REPOS_PER_LANGUAGE = 250

def search_repositories(language, per_page=100, page=1):
    query = f"language:{language}"
    url = f"{GITHUB_API_URL}/search/repositories?q={query}&sort=stars&order=desc&per_page={per_page}&page={page}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"Error fetching repositories for language {language}: {response.status_code}")
        return []

def check_required_files(repo_full_name, required_files):
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/contents"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        contents = response.json()
        file_names = [item['name'] for item in contents]
        return all(req_file in file_names for req_file in required_files)
    else:
        print(f"Error fetching contents for repository {repo_full_name}: {response.status_code}")
        return False

def fork_repository(repo_full_name):
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/forks"
    response = requests.post(url, headers=HEADERS)
    if response.status_code == 202:
        print(f"Successfully forked: {repo_full_name}")
        return True
    else:
        print(f"Error forking repository {repo_full_name}: {response.status_code} - {response.text}")
        return False

def main():
    total_forked = 0

    for language, required_files in LANGUAGES_AND_FILES.items():
        repos_forked = 0
        page = 1

        while repos_forked < NUM_REPOS_PER_LANGUAGE:
            repositories = search_repositories(language, per_page=100, page=page)
            if not repositories:
                break

            for repo in repositories:
                if repos_forked >= NUM_REPOS_PER_LANGUAGE:
                    break

                repo_full_name = repo['full_name']
                # Check if the repository contains the required files
                if check_required_files(repo_full_name, required_files):
                    if fork_repository(repo_full_name):
                        repos_forked += 1
                        total_forked += 1

                        # Random delay to avoid hitting rate limits
                        time.sleep(random.uniform(1, 3))

            page += 1

            # Avoid overwhelming the GitHub API (respect rate limits)
            time.sleep(10)

    print(f"Total repositories forked: {total_forked}")

if __name__ == "__main__":
    main()
