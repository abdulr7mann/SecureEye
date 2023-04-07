import os
import shutil
import git
import requests
from tqdm import tqdm

# GitHub API endpoint for searching repositories
GITHUB_API_SEARCH_URL = "https://api.github.com/search/repositories"

# Your GitHub username and access token
GITHUB_USERNAME = "your_username"
GITHUB_ACCESS_TOKEN = "your_access_token"

# Directory to save cloned repositories
CLONE_DIRECTORY = "/path/to/clone/directory"

# Query parameters for searching repositories
query_params = {
    "q": "language:python",  # Only search for Python repositories
    "sort": "stars",  # Sort by stars
    "order": "desc",  # Descending order
    "per_page": 100  # Number of results per page
}

# HTTP headers for GitHub API requests
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_ACCESS_TOKEN}"
}

# Make the initial request to the GitHub API
response = requests.get(GITHUB_API_SEARCH_URL, params=query_params, headers=headers)

# Get the total number of pages to iterate through
total_pages = response.json()["total_count"] // query_params["per_page"] + 1

# Iterate through each page of search results
for page in range(1, total_pages + 1):
    query_params["page"] = page
    response = requests.get(GITHUB_API_SEARCH_URL, params=query_params, headers=headers)
    results = response.json()["items"]
    
    # Iterate through each repository on the page
    for repo in tqdm(results, desc=f"Page {page}/{total_pages}"):
        repo_name = repo["full_name"]
        clone_directory = os.path.join(CLONE_DIRECTORY, repo_name)
        
        # Skip if the repository has already been cloned
        if os.path.isdir(clone_directory):
            continue
        
        # Clone the repository
        try:
            git.Repo.clone_from(repo["clone_url"], clone_directory)
        except Exception as e:
            print(f"Failed to clone {repo_name}: {e}")
