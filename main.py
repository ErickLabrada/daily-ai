import asyncio

from scrapper.github.scrapper import get_commits_since_last_daily,get_commit_diff
from scrapper.kanban.scrapper import get_my_tasks
from scrapper.kanban.sesion import auto_login
from llm.llm import generate_daily_report
from tts.tts import text_to_speech


async def get_data(branch ="dev", time=1):
    auto_login()
    print("Fetching Kanban tasks...")
    kanban_tasks = await get_my_tasks(user_id="206")

    print("Fetching Git activity...")
    raw_commits = await get_commits_since_last_daily(branch, time)
    
    processed_git_data = []
    for c in raw_commits:
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
    Las actividades que estaré haciendo son:
    -Conectar los modulos ya terminados
    -Implementar los valores de atributos variantes
    -Empezar a trabajar en el modulo de racs

    En ese orden

    """

    kanban_tasks, processed_git_data = await get_data("feat/ECOM-EMRQ05HU023", 4)
    report = await generate_report(kanban_tasks,processed_git_data,extra_data)
#    report = """Sin novedades por mi parte"""
    audio = await generate_audio(report)

if __name__ == "__main__":
    asyncio.run(main())
