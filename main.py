import asyncio

from scrapper.github.scrapper import get_commits_since_last_daily,get_commit_diff
from scrapper.kanban.scrapper import get_my_tasks
from scrapper.kanban.sesion import auto_login
from llm.llm import generate_daily_report
from tts.tts import text_to_speech
import subprocess

async def main():
    auto_login()

    print("Fetching Kanban tasks...")
    kanban_tasks = await get_my_tasks(user_id="206")

    print("Fetching Git activity...")
    raw_commits = await get_commits_since_last_daily("feat/ECOM-EMRQ05HU023", 5)
    
    processed_git_data = []
    for c in raw_commits:
        sha = c.get('id')
        diffs = await get_commit_diff(sha)
        processed_git_data.append({
            "title": c.get('title'),
            "files_touched": diffs
        })

    print("Generating Daily Report...")
    report = await generate_daily_report(processed_git_data, kanban_tasks)
    
    print("\n--- YOUR DAILY REPORT ---\n")
    print(report)

    print("Converting report to speech...")
    audio_file = await text_to_speech(report)
    print("Preparing Virtual Microphone...")
    
    setup_commands = [
        "pactl load-module module-null-sink sink_name=VirtualMic sink_properties=device.description=Virtual_Microphone_Sink",
        "pactl load-module module-loopback source=VirtualMic.monitor sink=VirtualMic"
    ]

        # Find your headphone sink name first with: pactl list sinks short
    #headphone_sink = "alsa_output.pci-0000_00_1f.3.analog-stereo" # Example name

    # Add this to your setup_commands
    #setup_commands.append(f"pactl load-module module-loopback source=VirtualMic.monitor sink={headphone_sink}")
    
    module_ids = []
    for cmd in setup_commands:
        # Changed 'capture_with' to 'capture_output'
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        if result.returncode == 0:
            # pactl returns the module ID on success, which we need for cleanup
            module_ids.append(result.stdout.strip())
        else:
            print(f"Warning: Failed to load module. Error: {result.stderr}")
    try:
        print(f"Streaming {audio_file} to VirtualMic...")
        # 2. STREAM: Run ffmpeg
        # -re: Read input at native frame rate
        # -f pulse: Output to PulseAudio
        subprocess.run([
            "ffmpeg", "-re", "-i", audio_file, 
            "-f", "pulse", "VirtualMic"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\nStopping stream...")
    finally:
        # 3. TEARDOWN: Remove the virtual modules so they don't clutter your system
        print("Cleaning up virtual audio devices...")
        for mid in module_ids:
            subprocess.run(["pactl", "unload-module", mid])
if __name__ == "__main__":
    asyncio.run(main())