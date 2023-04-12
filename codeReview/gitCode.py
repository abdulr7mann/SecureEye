import git
import re
import string
import os
import shutil
import sys
import time
import datetime
import chardet
import fnmatch
from git import RemoteProgress
import codeReview

# Define the cost per token and per second
COST_PER_TOKEN = 0.000002
COST_PER_SECOND = 0.005555
# Calculate the number of seconds
num_seconds = 0
# Calculate the total cost of tokens
num_tokens = 0

start_time = time.time()
# Repository URL
repo_url = (f"https://github.com/snoopysecurity/Vulnerable-Code-Snippets.git")
# repo_url = (
#     "https://github.com/jadz/php-sploits.git"
#     "https://github.com/django-cms/django-cms.git",
#     "https://github.com/snoopysecurity/Vulnerable-Code-Snippets.git",
#     "https://github.com/Stealerium/Stealerium.git",
#     "https://github.com/rubennati/vulnerable-php-code-examples.git"
# )

# split the repo URL to get the repo name
repo_name = repo_url.split("/")[-1].replace(".git", "")
# absolute path to the current working directory
current_path = os.getcwd()
# Create a path to a temporary directory using the random string
local_repo_path = f"{current_path}/{repo_name}"
# Define the blacklist of file names
blacklist = (
    "*.md",
    "changelog.txt",
    "*.txt",
    "*.ico",
    "README",
    "LICENSE",
    "*.csproj",
    "*.sln",
    ".git*",
    ".DS_Store",
    ".idea",
    ".vscode",
    "node_modules",
    "bower_components",
    "package-lock.json",
    "yarn.lock",
    "*file.js",
    "*config.js",
    "composer.*",
    "Gemfile*",
    "Procfile",
    ".travis.yml",
    ".gitlab-ci.yml",
    ".circleci",
    ".github",
    ".editorconfig",
    ".htaccess",
    ".htpasswd",
    "nginx.conf",
    "docker-compose.yml",
    "Jenkinsfile",
    "Makefile",
    ".mailmap"
)

# Check if the local_repo_path directory exists
if os.path.isdir(local_repo_path):
    # If the directory exists, pull the latest changes
    repo = git.Repo(local_repo_path)
    origin = repo.remote(name='origin')
    origin.pull()
    print(f"Repository successfully updated: {repo_url} --> {local_repo_path}")
    print(f"Creating report folder: {current_path}/report/{repo_name}")
    os.mkdir(f'{current_path}/report/{repo_name}')
else:
    # If the directory does not exist, clone the repository
    try:
        git.Repo.clone_from(repo_url, local_repo_path)
        print(f"Cloning is successful: {repo_url} --> {local_repo_path}")
        print(f"Creating report folder: {current_path}/report/{repo_name}")
        os.mkdir(f'{current_path}/report/{repo_name}')
    except git.exc.GitCommandError as e:
        print(f"An error occurred while cloning the repository: {e}")
        exit(1)
    except KeyboardInterrupt:
        # Handle the exception
        print("KeyboardInterrupt caught. Exiting...")


# Loop through all files in the repository
try:
    repo = git.Repo(local_repo_path)
except git.exc.NoSuchPathError as e:
    print(f"An error occurred while accessing the repository: {e}")
    exit(1)
except KeyboardInterrupt:
    # Handle the exception
    print("KeyboardInterrupt caught. Exiting...")


# converting all elements to lowercase
blacklist = [item.lower() for item in blacklist]
# Iterating over all the files in a repository's tree object.
for file in repo.tree().traverse():
    file_name = file.name
    # Check if the file is a blob (i.e., a file)
    if file.type == "blob":
        # Check if the file name matches any of the blacklisted file names
        if any(fnmatch.fnmatch(file_name.lower(), pattern) for pattern in blacklist):
            print(f"Excluding file: {file_name}")
            continue
        # Get the contents of the file
        try:
            print(f"Reading file's content: {file_name}")
            file_contents = file.data_stream.read()
            detected_encoding = chardet.detect(file_contents)
            file_contents = file_contents.decode(detected_encoding['encoding'])
            print(
                f"Detecting file's content encoding: {detected_encoding['encoding']}")
        except UnicodeDecodeError as e:
            print(f"An error occurred while reading file contents: {e}")
            continue
        except KeyboardInterrupt:
            # Handle the exception
            print("KeyboardInterrupt caught. Exiting...")
        # Analyze the file contents using ChatGPT
        start_time = time.time()
        analysis = ""
        analysis = codeReview.codeReviewAi.analyze_file_contents(
            file_contents, file_name)

        if analysis is None:
            continue
        # Do something with the analysis here (e.g., print it)
        # Open the output file in write append
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        with open(f'{current_path}/report/{repo_name}/{repo_name}-{now}.md', 'a') as reporting:
            # Redirect the standard output to the file
            sys.stdout = reporting
            end_time = time.time()
            time_consumed = end_time - start_time
            # Calculate the number of seconds
            num_seconds = time_consumed
            # Calculate the total cost of tokens
            num_tokens = int(analysis['usage']['total_tokens'])
            token_cost = num_tokens * COST_PER_TOKEN
            # Calculate the total cost of time
            time_cost = num_seconds * COST_PER_SECOND
            # Calculate the total cost
            total_cost = token_cost + time_cost
            print(f"### Total time consumed: {time_consumed/60:.0f} minutes")
            print(f"### Total tokens used: {analysis['usage']['total_tokens']}")
            print(f"### Total cost is: ${total_cost:.2f}")
            print(f"### Repository: {repo_name}\n### File: {file_name}")
            print(f'{analysis["choices"][0]["message"]["content"]}\n\n\n')
            # Redirect the standard output back to the terminal
            sys.stdout = sys.__stdout__

# Delete the temporary directory
try:
    print(f"Analyzing is done\nDeleting repository folder")
    shutil.rmtree(local_repo_path)
except OSError as e:
    print(f"An error occurred while deleting the temporary directory: {e}")
