# codeReview/gitCode.py

import git
import os
import sys
import time
import datetime
import chardet
import fnmatch
import shutil
import zipfile
from . import codeReviewAi

# Define the cost per token and per second
COST_PER_TOKEN = 0.000002
COST_PER_SECOND = 0.005555

# Define the blacklist of file names
BLACKLIST = [
    "*.md", "changelog.txt", "*.txt", "*.ico", "README", "LICENSE",
    "*.csproj", "*.sln", ".git*", ".DS_Store", ".idea", ".vscode",
    "node_modules", "bower_components", "package-lock.json", "yarn.lock",
    "*file.js", "*config.js", "composer.*", "Gemfile*", "Procfile",
    ".travis.yml", ".gitlab-ci.yml", ".circleci", ".github", ".editorconfig",
    ".htaccess", ".htpasswd", "nginx.conf", "docker-compose.yml", "Jenkinsfile",
    "Makefile", ".mailmap"
]

output_messages = []

def analyze_repository(repo_url):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    current_path = os.getcwd()
    local_repo_path = f"{current_path}/{repo_name}"

    if os.path.isdir(local_repo_path):
        repo = git.Repo(local_repo_path)
        origin = repo.remote(name='origin')
        origin.pull()
        output_messages.append(f"Repository successfully updated: {repo_url} --> {local_repo_path}")
    else:
        try:
            git.Repo.clone_from(repo_url, local_repo_path)
            output_messages.append(f"Cloning is successful: {repo_url} --> {local_repo_path}")
        except git.exc.GitCommandError as e:
            output_messages.append(f"An error occurred while cloning the repository: {e}")
            sys.exit(1)

    analyze_files(local_repo_path)
    shutil.rmtree(local_repo_path)  # Clean up the cloned repository

def analyze_local_path(local_path):
    if local_path.endswith('.zip'):
        repo_name = os.path.basename(local_path).replace('.zip', '')
        extract_path = os.path.join(os.getcwd(), repo_name)
        with zipfile.ZipFile(local_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        analyze_files(extract_path)
        shutil.rmtree(extract_path)  # Clean up the extracted files
    elif os.path.isdir(local_path):
        analyze_files(local_path)
    else:
        output_messages.append(f"Invalid path: {local_path}")
        sys.exit(1)
        
def analyze_files(path):
    current_path = os.getcwd()
    repo_name = os.path.basename(path)
    report_dir = f'{current_path}/report/{repo_name}'

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    blacklist = [item.lower() for item in BLACKLIST]

    for root, _, files in os.walk(path):
        for file in files:
            if any(fnmatch.fnmatch(file.lower(), pattern) for pattern in blacklist):
                output_messages.append(f"Excluding file: {file}")
                continue
            
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                file_contents = f.read()

            detected_encoding = chardet.detect(file_contents)['encoding']
            file_contents = file_contents.decode(detected_encoding or 'utf-8')

            try:
                start_time = time.time()
                analysis = codeReviewAi.analyze_file_contents(file_contents, file)

                if analysis is None:
                    continue

                now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                report_file_path = f'{report_dir}/{repo_name}-{now}.md'
                with open(report_file_path, 'a') as reporting:
                    sys.stdout = reporting
                    
                    end_time = time.time()
                    time_consumed = end_time - start_time
                    num_seconds = time_consumed
                    
                    num_tokens = int(analysis['usage']['total_tokens'])
                    token_cost = num_tokens * COST_PER_TOKEN
                    time_cost = num_seconds * COST_PER_SECOND
                    total_cost = token_cost + time_cost
                    
                    print(f"### Total time consumed: {time_consumed:.2f} seconds")
                    print(f"### Total tokens used: {num_tokens}")
                    print(f"### Total cost is: ${total_cost:.2f}")
                    print(f"### File: {file_path}")
                    print(f'{analysis["choices"][0]["message"]["content"]}\n\n\n')
                    
                    sys.stdout = sys.__stdout__
                    output_messages.append(f"Analyzed {file_path}: {analysis['choices'][0]['message']['content']}")

            except KeyboardInterrupt:
                print("\nAnalysis interrupted by user. Exiting...")
                sys.exit()
                return
