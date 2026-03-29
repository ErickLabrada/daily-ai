import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

# 1. Clean the base URL
GITLAB_URL = os.getenv("GITLAB_URL", "https://git.sully.app").rstrip("/")
if not GITLAB_URL.startswith("http"):
    GITLAB_URL = f"https://{GITLAB_URL}"

PROJECT_ID = os.getenv("PROJECT_ID", "381")
TOKEN = os.getenv("GITLAB_TOKEN")

async def get_today_commits(branch="main"):
    # Build the URL carefully
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/commits"
    
    headers = {"PRIVATE-TOKEN": TOKEN}
    params = {
        "ref_name": branch,
        # You can add 'since': '2026-03-28T00:00:00Z' here later
    }

    print(f"DEBUG: Fetching from {url}...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"❌ API Error: {e.response.status_code}")
            return []
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return []

async def get_commit_diff(commit_sha):
    # 1. Immediate safety check
    if not commit_sha:
        print("⚠️ No commit SHA provided to get_commit_diff.")
        return []

    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/commits/{commit_sha}/diff"
    headers = {"PRIVATE-TOKEN": TOKEN}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            # 2. Check for actual API success before parsing JSON
            if response.status_code != 200:
                print(f"❌ GitLab API Error ({response.status_code}) for {commit_sha[:8]}")
                return []
                
            data = response.json()
            if isinstance(data, list):
                return [d.get('new_path') for d in data if 'new_path' in d]
            
            return []
            
        except Exception as e:
            # Use a fallback if commit_sha is somehow weird here
            sha_display = str(commit_sha)[:8] if commit_sha else "Unknown"
            print(f"❌ Failed to fetch diff for {sha_display}: {e}")
            return []

async def main():
    commits = await get_today_commits("feat/ECOM-EMRQ05HU023")
    
    for commit in commits:
        # Extract the ID string from the dictionary
        sha = commit.get('id') 
        
        print(f"[{commit.get('short_id')}] {commit.get('title')}")
        
        # Now 'sha' is a string, and get_commit_diff will work!
        diffs = await get_commit_diff(sha)
        
        if diffs:
            print(f"   Files touched: {', '.join(diffs[:3])}...")


if __name__ == "__main__":
    asyncio.run(main())