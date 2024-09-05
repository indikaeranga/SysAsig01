from github import Github
import io
import csv
import os
import fnmatch  # Import fnmatch module for pattern matching
from urllib.parse import urlparse  # Import to parse the PR URL

# Replace with your personal access token
GITHUB_TOKEN = 'token'
REPO_OWNER = 'indikaeranga'
REPO_NAME = 'SysAsig01'
BASE_BRANCH = 'main'  # Replace with the appropriate base branch for the PR
BODY = 'This is an auto-generated pull request.'  # Body for the PR

# Function to check if a pull request already exists for the branch
def pr_exists_for_branch(branch_name):
    open_prs = Github(GITHUB_TOKEN).get_repo(f"{REPO_OWNER}/{REPO_NAME}").get_pulls(state='open', base=BASE_BRANCH)
    for pr in open_prs:
        if pr.head.ref == branch_name:
            return pr
    return None

def main():
    # Authenticate using the personal access token
    g = Github(GITHUB_TOKEN)
    
    # Get the repository
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    
    # List all branches
    branches = repo.get_branches()

    report = [] 
    
    # Define the branch patterns to look for
    branch_patterns = ['*infra*', '*okra*', '*de*']
    
    # Define the commit message patterns to look for
    commit_message_patterns = [
        "*feat(cicd): add cicd folder*",
        "*feat(cicd): update cicd folder*",
        "*refactor(okra): add Terraform files -*",
        "*feat(okra): update Terraform files -*"
    ]

    for branch in branches:
        print(f"Checking branch: {branch.name}")  # Print the branch name to the terminal

        # Check if the branch name matches any of the specified patterns
        if any(fnmatch.fnmatch(branch.name, pattern) for pattern in branch_patterns):
            # Get the latest commit on the branch
            commit = repo.get_branch(branch.name).commit
            last_commit = repo.get_commit(commit.sha)
            last_commit_message = last_commit.commit.message

            # Check if the commit message matches any of the specified patterns
            if any(fnmatch.fnmatch(last_commit_message, pattern) for pattern in commit_message_patterns):
                # Check if a pull request already exists for this branch
                existing_pr = pr_exists_for_branch(branch.name)
                pr_number = ''
                pr_link = ''

                if existing_pr:
                    pr_number = existing_pr.number
                    pr_link = existing_pr.html_url
                else:
                    # Create a new pull request
                    pr = repo.create_pull(
                        title=last_commit_message,
                        body=BODY,
                        head=branch.name,
                        base=BASE_BRANCH
                    )

                    pr_link = pr.html_url
                    pr_number = pr.number

                # Add to report
                report.append({
                    'Branch Name': branch.name,
                    'Last commit user': commit.commit.author.name,
                    'Last commit Date': commit.commit.committer.date,
                    'Last commit Message': last_commit_message,
                    'PR Number': pr_number,
                    'PR Link': pr_link
                })

    # Write the report to a CSV file only if there are matching branches and commit messages
    if report:
        csv_buffer = io.StringIO()
        csv_writer = csv.DictWriter(csv_buffer, fieldnames=['Branch Name', 'Last commit user', 'Last commit Date', 'Last commit Message', 'PR Number', 'PR Link'])
        csv_writer.writeheader()
        csv_writer.writerows(report)

        csv_data = csv_buffer.getvalue()
        file_path = 'Documents/Last_commited_user.csv'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, mode='w', newline='') as file:
            file.write(csv_data)

if __name__ == '__main__':
    main()
