# 1. Create virtual sink

pactl load-module module-null-sink \
  sink_name=virtual_sink \
  sink_properties=device.description=Virtual_Sink

# 2. Create virtual microphone (source from sink monitor)

pactl load-module module-remap-source \
  master=virtual_sink.monitor \
  source_name=virtual_mic \
  source_properties=device.description=Virtual_Microphone

# 3. Send audio into the sink (IMPORTANT FIX HERE)

ffmpeg -re -i daily_report.mp3 -f pulse virtual_sink