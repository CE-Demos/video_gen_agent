# utils/video_utils.py
from moviepy.editor import VideoFileClip, concatenate_videoclips

def concatenate_videos(video_paths, output_path="concatenated_video.mp4"):
    """Concatenates multiple video files."""
    clips = [VideoFileClip(path) for path in video_paths]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    for clip in clips:
        clip.close()
    return output_path