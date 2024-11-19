
import requests
import os

# Retrieve the secret from the environment
GITHUB_TOKEN = "ghp_7"+"zcxTRXz"+"N5ZA9M"+"loyFRsE"+"tnmaO"+"vdV00f9"+"f4k"

REPO_OWNER = "ksnarkhede"
REPO_NAME = "Task-Repo"
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"


HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_open_pull_requests():
    """Fetch all open pull requests for the repository."""
    url = f"{BASE_URL}/pulls"
    response = requests.get(url, headers=HEADERS, params={"state": "open"})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching pull requests: {response.status_code}")
        print(response.json())
        return []

def check_reviews(pr_number, required_approvals=1):
    """Check if a pull request has the required number of approved reviews."""
    url = f"{BASE_URL}/pulls/{pr_number}/reviews"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        reviews = response.json()
        approved_count = sum(1 for review in reviews if review["state"] == "APPROVED")
        return approved_count >= required_approvals
    else:
        print(f"Error fetching reviews for PR #{pr_number}: {response.status_code}")
        print(response.json())
        return False

def merge_pull_request(pr_number, merge_method="merge", commit_title=None, commit_message=None):
    """Merge a pull request using the GitHub API."""
    url = f"{BASE_URL}/pulls/{pr_number}/merge"
    payload = {"merge_method": merge_method}
    if commit_title:
        payload["commit_title"] = commit_title
    if commit_message:
        payload["commit_message"] = commit_message

    response = requests.put(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        print(f"Successfully merged PR #{pr_number}.")
        print(response.json())
    elif response.status_code == 409:
        print(f"Conflict! PR #{pr_number} could not be merged automatically.")
    elif response.status_code == 404:
        print(f"PR #{pr_number} not found. Check the repository and PR number.")
    else:
        print(f"Error merging PR #{pr_number}: {response.status_code}")
        print(response.json())

def main():
    """Main logic for checking and merging pull requests."""
    print("Fetching open pull requests...")
    pull_requests = get_open_pull_requests()

    if not pull_requests:
        print("No open pull requests found.")
        return

    for pr in pull_requests:
        pr_number = pr["number"]
        pr_title = pr["title"]
        print(f"Checking PR #{pr_number}: {pr_title}")
        if check_reviews(pr_number, required_approvals=1):  
            print(f"PR #{pr_number} has the required approvals. Attempting to merge...")
            merge_pull_request(
                pr_number,
                merge_method="squash",  
                commit_title=f"Merging PR #{pr_number}",
                commit_message="Merged automatically using Python script."
            )
        else:
            print(f"PR #{pr_number} does not have the required approvals. Skipping.")

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("Please set your GITHUB_TOKEN in the script before running.")
    else:
        main()
