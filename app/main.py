from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.github_utils import get_pr_details, post_formal_review
from app.agents import run_agent_crew

app = FastAPI(
    title="Lyzr AI Code Reviewer",
    description="Automated PR Review Agent using Gemini 1.5 Flash & CrewAI"
)

class PRRequest(BaseModel):
    github_url: str
    # Example: "https://github.com/your-username/your-repo/pull/1"

@app.get("/")
def home():
    return {"message": "Lyzr AI Agent is Running 🚀"}

@app.post("/review")
def review_pr(request: PRRequest):
    # 1. Parse the URL
    try:
        # Extracts 'owner/repo' and 'pr_number' from URL
        parts = request.github_url.split("github.com/")[-1].split("/")
        repo_name = f"{parts[0]}/{parts[1]}"
        pr_number = int(parts[3])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid GitHub Pull Request URL.")

    print(f"🔍 Analyzing PR: {repo_name} #{pr_number}")

    # 2. Fetch Code
    pr_obj, diff_text = get_pr_details(repo_name, pr_number)
    
    if not pr_obj:
        raise HTTPException(status_code=404, detail="Repo not found.")
    
    if not diff_text:
        return {"status": "Skipped", "message": "No code changes found in this PR."}

    # 3. Run AI Crew
    print("🤖 AI Crew starting...")
    review_result = run_agent_crew(diff_text)
    
    # 4. Parse Verdict (Simple Logic)
    action = "COMMENT"
    if "VERDICT: APPROVE" in review_result:
        action = "APPROVE"
    elif "VERDICT: REQUEST_CHANGES" in review_result:
        action = "REQUEST_CHANGES"

    # 5. Post Result to GitHub
    post_formal_review(pr_obj, review_result, action)

    return {
        "status": "Success", 
        "verdict": action, 
        "review": review_result
    }