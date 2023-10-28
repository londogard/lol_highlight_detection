from pathlib import Path
from typing import Dict, List
from moviepy.editor import VideoFileClip, concatenate_videoclips
import streamlit as st


@st.cache_data
def build_video(orig_vid: str | Path, timestamps: List[Dict[str, str]], out: Path):
    # timestamps = [{"start": "00:01:23", "end": "00:02:45"}]
    video_clips = []
    video = VideoFileClip(orig_vid)

    # Extract video clips for each timestamp event
    for timestamp in timestamps:
        clip = video.subclip(timestamp["start"], timestamp["end"])
        video_clips.append(clip)

    # Apply crossfade transition between video clips
    # transition_duration = 1.0
    # transition_clips = []
    # for i in range(len(video_clips) - 1):
    #     transition_clip = crossfadein(
    #         video_clips[i], video_clips[i + 1], duration=transition_duration
    #     )
    #     transition_clips.append(transition_clip)

    # Concatenate the video clips with transitions
    final_clip = concatenate_videoclips(video_clips)

    # Write the final concatenated movie to a file
    final_clip.write_videofile(str(out))
