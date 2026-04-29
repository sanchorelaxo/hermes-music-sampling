# Export an Ardour session to WAV
from skills.daw_master.ardour_automator import pipeline

pipeline.export(
    session_path="project.ardour",
    output_path="mix.wav",
    format="wav"
)
