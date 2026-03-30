# 1. Create the virtual speaker (sink)

pactl load-module module-null-sink sink_name=VirtualMic sink_properties=device.description=Virtual_Microphone_Sink

# 2. Create a "loopback" so the sink acts as a source (mic)

pactl load-module module-remap-source master=VirtualMic.monitor source_name=VirtualMic_Source source_properties=device.description=Virtual_Microphone

# 3. Stream the MP3 to the Virtual Mic

ffmpeg -re -i daily_report.mp3 -f pulse "VirtualMic"



