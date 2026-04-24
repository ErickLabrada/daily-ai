import asyncio

from scrapper.github.scrapper import get_commits_since_last_daily,get_commit_diff
from scrapper.kanban.scrapper import get_my_tasks
from scrapper.kanban.sesion import auto_login
from llm.llm import generate_daily_report
from tts.tts import text_to_speech


async def get_data(branches =["dev"], time=1):
    auto_login()
    print("Fetching Kanban tasks...")
    kanban_tasks = await get_my_tasks(user_id="206")
    print("Fetching Git activity...")
    raw_commits = await get_commits_since_last_daily(branches, time)
    
    processed_git_data = []
    for commit in raw_commits:
        for c in commit:
            sha = c.get('id')
            diffs = await get_commit_diff(sha)
            processed_git_data.append({
                "title": c.get('title'),
                "files_touched": diffs
            })
    return kanban_tasks, processed_git_data


async def generate_report(kanban_tasks, processed_git_data,extra_data=""):

    print("Generating Daily Report...")
    report = await generate_daily_report(processed_git_data, kanban_tasks,extra_data)    
    print("\n--- YOUR DAILY REPORT ---\n")
    print(report)
    return report 
    

async def generate_audio(report):
    print("Converting report to speech...")
    audio_file = await text_to_speech(report)
    return audio_file


async def main():
    extra_data = """
    El backend de todos los modulos que se mencionan fueron terminados
    """

    branches=[
        "feat/back-variants",
        "feat/back-products",
        "feat/composite",
        "feat/back-attributes",
    ]

    kanban_tasks, processed_git_data = await get_data(branches, 2)
    report = await generate_report(kanban_tasks,processed_git_data,extra_data)

    answer = input("Create speech?")

    if answer == "y":
        audio = await generate_audio(report)

if __name__ == "__main__":

    asyncio.run(main())
