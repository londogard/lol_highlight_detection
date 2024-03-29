from pathlib import Path
from typing import Dict, List
from moviepy.editor import VideoFileClip, concatenate_videoclips


def get_vid_path(
    orig_vid: str | Path, timestamps: List[Dict[str, str]], out: Path
) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    vid_name = Path(orig_vid).name
    out_path = out / (vid_name + f"_{hash(str(timestamps))}.mp4")

    return out_path


def build_video(orig_vid: str | Path, timestamps: List[Dict[str, str]], out_path: Path):
    # timestamps = [{"start": "00:01:23", "end": "00:02:45"}]
    if out_path.exists():
        return out_path

    video_clips = []
    video = VideoFileClip(orig_vid)

    # Extract video clips for each timestamp event
    for timestamp in timestamps:
        clip = video.subclip(timestamp["start"], timestamp["end"])
        video_clips.append(clip)

    # Concatenate the video clips with transitions
    final_clip = concatenate_videoclips(video_clips)

    # Write the final concatenated movie to a file
    final_clip.write_videofile(str(out_path))
    return out_path
