import os
import httpx
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone


load_dotenv()

GITLAB_URL = os.getenv("GITLAB_URL", "https://git.sully.app").rstrip("/")
if not GITLAB_URL.startswith("http"):
    GITLAB_URL = f"https://{GITLAB_URL}"

PROJECT_ID = os.getenv("PROJECT_ID", "381")
TOKEN = os.getenv("GITLAB_TOKEN")

def get_past_date_iso(days_ago=1):
    target_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
    
    target_date = target_date.replace(hour=17, minute=30, second=0, microsecond=0)
    print(target_date)
    return target_date.strftime('%Y-%m-%dT%H:%M:%SZ')

async def get_commits_since_last_daily(branch="dev", days_to_look_back=1):

    since_date = get_past_date_iso(days_to_look_back)
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/commits"
    
    headers = {"PRIVATE-TOKEN": TOKEN}
    params = {
        "ref_name": branch,
        'since': since_date

    }

    print(f"DEBUG: Fetching from {url}...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            raw_commits = response.json()
            print("===========RAW COMMITS===========")
            print(raw_commits)
            filtered_commits = [
                c for c in raw_commits 
                if c.get("author_email") == "erick.labrada@mediaaerea.mx" or c.get("author_name")=="Erick Labrada"
            ]
            print("===========FILTERED COMMITS===========")
            print(f"Found {len(filtered_commits)} commits by you.")
            print(filtered_commits)
            return filtered_commits

        except httpx.HTTPStatusError as e:
            print(f"API Error: {e.response.status_code}")
            return []
        except Exception as e:
            print(f"Connection Error: {e}")
            return []

async def get_commit_diff(commit_sha):
    # 1. Immediate safety check
    if not commit_sha:
        print("No commit SHA provided to get_commit_diff.")
        return []

    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/commits/{commit_sha}/diff"
    headers = {"PRIVATE-TOKEN": TOKEN}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            # 2. Check for actual API success before parsing JSON
            if response.status_code != 200:
                print(f"GitLab API Error ({response.status_code}) for {commit_sha[:8]}")
                return []
                
            data = response.json()
            if isinstance(data, list):
                return [d.get('new_path') for d in data if 'new_path' in d]
            
            return []
            
        except Exception as e:

            sha_display = str(commit_sha)[:8] if commit_sha else "Unknown"
            print(f"Failed to fetch diff for {sha_display}: {e}")
            return []

async def main():
    commits = await get_commits_since_last_daily("feat/ECOM-EMRQ05HU023", days_to_look_back=1)
    
    for commit in commits:

        sha = commit.get('id') 
        
        print(f"[{commit.get('short_id')}] {commit.get('title')}")
        

        diffs = await get_commit_diff(sha)
        
        if diffs:
            print(f"   Files touched: {', '.join(diffs[:3])}...")


if __name__ == "__main__":
    asyncio.run(main())