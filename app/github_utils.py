import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

# Initialize GitHub
g = Github(os.getenv("GITHUB_TOKEN"))

def get_pr_details(repo_name, pr_number):
    """
    Fetches the PR object and the diff text.
    """
    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        diff_text = ""
        # Limit to 5 files to prevent context overflow (even with Gemini's large window, let's be safe)
        for file in pr.get_files()[:5]:
            if file.status != "removed":
                diff_text += f"## File: {file.filename}\n```\n{file.patch}\n```\n\n"
        
        return pr, diff_text
    except Exception as e:
        print(f"Error fetching PR: {e}")
        return None, None

def post_formal_review(pr, review_content, action="COMMENT"):
    """
    Posts a FORMAL review status to GitHub.
    Action must be: "APPROVE", "REQUEST_CHANGES", or "COMMENT"
    """
    try:
        # Create the review
        pr.create_review(body=review_content, event=action)
        print(f"✅ Posted {action} to PR #{pr.number}")
        return True
    except Exception as e:
        print(f"❌ Failed to post review: {e}")
        return False