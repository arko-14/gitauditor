import os
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Setup Gemini 1.5 Flash
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    verbose=True,
    temperature=0.1,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def run_agent_crew(diff_text):
    # Agent 1: The Tech Lead (Strict Reviewer)
    reviewer = Agent(
        role='Senior Backend Engineer',
        goal='Analyze code for critical bugs, security flaws, and bad practices.',
        backstory="""You are a strict code reviewer. You hate logical errors, 
        security risks (like SQL injection), and messy code. 
        You focus on the Code Diff provided.""",
        llm=llm,
        verbose=True
    )

    # Agent 2: The Release Manager (Decision Maker)
    manager = Agent(
        role='Release Manager',
        goal='Decide if the PR should be APPROVED or REQUEST_CHANGES.',
        backstory="""You read the technical review and make the final call. 
        If there are bugs/security issues, you REQUEST_CHANGES. 
        If it is just style nitpicks or clean code, you APPROVE.""",
        llm=llm,
        verbose=True
    )

    # Task 1: Find Bugs
    review_task = Task(
        description=f"Analyze this code diff:\n\n{diff_text}",
        expected_output="A list of technical issues, bugs, and security risks.",
        agent=reviewer
    )

    # Task 2: Final Verdict
    # We strictly format the output so our API can read it easily
    decision_task = Task(
        description="""
        Based on the technical review, provide a final decision.
        
        YOUR OUTPUT MUST LOOK EXACTLY LIKE THIS:
        VERDICT: [APPROVE or REQUEST_CHANGES]
        SUMMARY: [1-2 sentences explaining why]
        DETAILS: [Bullet points of key issues]
        """,
        expected_output="Formatted decision string.",
        agent=manager,
        context=[review_task] # Wait for reviewer
    )

    crew = Crew(
        agents=[reviewer, manager],
        tasks=[review_task, decision_task],
        process=Process.sequential
    )

    result = crew.kickoff()
    return str(result)