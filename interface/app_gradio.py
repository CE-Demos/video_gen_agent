# interface/app.py
import gradio as gr
import requests
import os
from config import GCS_BUCKET_NAME
from utils.gcs_utils import upload_to_gcs, download_from_gcs, list_blobs
from utils.video_utils import concatenate_videos

# Assuming your agents are deployed and have accessible endpoints
PROMPT_READER_ENDPOINT = "YOUR_PROMPT_READER_AGENT_ENDPOINT"
VIDEO_GENERATOR_ENDPOINT = "YOUR_VIDEO_GENERATOR_AGENT_ENDPOINT"
PROMPT_SAVER_ENDPOINT = "YOUR_PROMPT_SAVER_AGENT_ENDPOINT"
PROMPT_RETRIEVER_ENDPOINT = "YOUR_PROMPT_RETRIEVER_AGENT_ENDPOINT"

def generate_video_from_prompt(prompt):
    payload = {"prompt": prompt}
    try:
        response = requests.post(PROMPT_READER_ENDPOINT, json=payload)
        response.raise_for_status()
        result = response.text # Or parse JSON if your agent returns JSON
        # Assuming video_generator_agent returns the path to the generated video
        video_path = requests.post(VIDEO_GENERATOR_ENDPOINT, json={"prompt": prompt}).text
        return result, video_path
    except requests.exceptions.RequestException as e:
        return f"Error communicating with agent: {e}", None

def download_video(video_path):
    if video_path and os.path.exists(video_path):
        return video_path
    else:
        return "Video not found."

def upload_videos_and_concatenate(video_files):
    if not video_files or len(video_files) < 2:
        return "Please upload at least two video files."
    video_paths = [file.name for file in video_files]
    output_path = concatenate_videos(video_paths)
    return output_path

def save_successful_prompt(prompt):
    payload = {"prompt": prompt}
    try:
        response = requests.post(PROMPT_SAVER_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error saving prompt: {e}"

def load_saved_prompts():
    try:
        response = requests.post(PROMPT_RETRIEVER_ENDPOINT)
        response.raise_for_status()
        prompts = response.json() # Assuming the agent returns a list of prompts in JSON
        return prompts
    except requests.exceptions.RequestException as e:
        return [f"Error retrieving prompts: {e}"]

with gr.Blocks() as demo:
    gr.Markdown("# Veo Video Generation Bot")

    with gr.Tab("Generate Video"):
        prompt_input = gr.Textbox(label="Enter Text Prompt for Video")
        generate_button = gr.Button("Generate Video")
        generation_output = gr.Textbox(label="Generation Status")
        video_output = gr.Video(label="Generated Video")
        save_prompt_checkbox = gr.Checkbox(label="Save this prompt?")
        save_prompt_button = gr.Button("Save Prompt")
        save_prompt_status = gr.Textbox(label="Save Status")

        generate_button.click(
            fn=generate_video_from_prompt,
            inputs=prompt_input,
            outputs=[generation_output, video_output]
        )
        save_prompt_button.click(
            fn=save_successful_prompt,
            inputs=prompt_input,
            outputs=save_prompt_status,
            condition=[save_prompt_checkbox]
        )
        video_output.download_button(download, "downloaded_video.mp4")

    with gr.Tab("Concatenate Videos"):
        video_upload = gr.Files(label="Upload Videos to Concatenate (at least 2)")
        concatenate_button = gr.Button("Concatenate Videos")
        concatenated_video_output = gr.Video(label="Concatenated Video")
        concatenate_button.click(
            fn=upload_videos_and_concatenate,
            inputs=video_upload,
            outputs=concatenated_video_output
        )
        concatenated_video_output.download_button(download, "concatenated_result.mp4")

    with gr.Tab("Saved Prompts"):
        saved_prompts_output = gr.List(label="Saved Prompts")
        load_prompts_button = gr.Button("Load Saved Prompts")
        load_prompts_button.click(fn=load_saved_prompts, outputs=saved_prompts_output)

demo.launch()