# interface/app.py
import gradio as gr
import requests
import os
import sys
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from config import GCS_BUCKET_NAME
from utils.gcs_utils import upload_to_gcs, download_from_gcs, list_blobs
from utils.video_utils import concatenate_videos
from agents.prompt_reader_agent import PromptReaderAgent

prompt_reader_agent = PromptReaderAgent()

def generate_video_from_prompt(prompt, aspect_ratio, allow_people):
    generation_result = prompt_reader_agent.process_prompt(prompt, aspect_ratio, allow_people)
    return generation_result.get("message", "Video generation initiated."), generation_result.get("video_path")

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

def save_successful_prompt(prompt, save_checkbox_value):
    if save_checkbox_value:
        # In this direct setup, you might directly call the prompt saver agent logic
        # or have the prompt reader agent handle saving as well.
        # For simplicity, let's assume direct call if you adapt the agent.
        # Replace with your actual saving mechanism if you have a separate agent.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"saved_prompts/prompt_{timestamp}.txt"
        file_path = f"temp_prompt_{timestamp}.txt"
        with open(file_path, 'w') as f:
            f.write(prompt)
        upload_to_gcs(GCS_BUCKET_NAME, file_path, blob_name)
        os.remove(file_path)
        return f"Prompt '{prompt}' saved to GCS."
    else:
        return "Prompt not saved."

def load_saved_prompts():
    blob_names = list_blobs(GCS_BUCKET_NAME, prefix="saved_prompts/")
    prompts = []
    for blob_name in blob_names:
        temp_file = f"temp_prompt_{blob_name.split('/')[-1]}"
        download_from_gcs(GCS_BUCKET_NAME, blob_name, temp_file)
        try:
            with open(temp_file, 'r') as f:
                prompts.append(f.read())
        except Exception as e:
            print(f"Error reading {blob_name}: {e}")
        finally:
            os.remove(temp_file)
    return prompts

with gr.Blocks() as demo:
    gr.Markdown("# Veo Video Generation Bot")

    with gr.Tab("Generate Video"):
        prompt_input = gr.Textbox(label="Enter Text Prompt for Video")
        aspect_ratio_dropdown = gr.Dropdown(
            choices=["16:9", "9:16"], label="Aspect Ratio", value="16:9"
        )
        allow_people_radio = gr.Radio(
            choices=["dont_allow", "allow_adult"], label="Allow People", value="dont_allow"
        )
        generate_button = gr.Button("Generate Video")
        generation_output = gr.Textbox(label="Generation Status")
        video_output = gr.Video(label="Generated Video")
        save_prompt_checkbox = gr.Checkbox(label="Save this prompt?")
        save_prompt_button = gr.Button("Save Prompt")
        save_prompt_status = gr.Textbox(label="Save Status")

        def handle_generation_click(prompt, aspect_ratio, allow_people):
            generation_result = prompt_reader_agent.process_prompt(prompt, aspect_ratio, allow_people)
            status = generation_result.get("message", "Video generation initiated.")
            video_path = generation_result.get("video_path")
            if video_path:
                if video_output is not None and hasattr(video_output, 'show_download_button'):
                    video_output.show_download_button("downloaded_video.mp4")
                else:
                    print("Warning: video_output is None or does not have show_download_button.")
            else:
                # Optionally handle the case where video generation failed
                if video_output is not None and hasattr(video_output, 'hide_download_button'):
                    video_output.hide_download_button()
                else:
                    print("Warning: video_output is None or does not have hide_download_button.")
            return status, video_path

        generate_button.click(
            fn=generate_video_from_prompt,
            inputs=[prompt_input, aspect_ratio_dropdown, allow_people_radio],
            outputs=[generation_output, video_output]
        )
        save_prompt_button.click(
            fn=save_successful_prompt,
            inputs=[prompt_input, save_prompt_checkbox],
            outputs=save_prompt_status
        )
        # video_output.show_download_button("downloaded_video.mp4")
        # handled separately in the handle function

    with gr.Tab("Concatenate Videos"):
        video_upload = gr.Files(label="Upload Videos to Concatenate (at least 2)")
        concatenate_button = gr.Button("Concatenate Videos")
        concatenated_video_output = gr.Video(label="Concatenated Video")

        def handle_concatenate_click(video_files):
            concatenated_path = upload_videos_and_concatenate(video_files)
            if concatenated_path:
                if concatenated_video_output is not None and hasattr(concatenated_video_output, 'show_download_button'):
                    concatenated_video_output.show_download_button("concatenated_result.mp4")
                else:
                    print("Warning: concatenated_video_output is None or does not have show_download_button.")
                return concatenated_path
            else:
                if concatenated_video_output is not None and hasattr(concatenated_video_output, 'hide_download_button'):
                    concatenated_video_output.hide_download_button()
                else:
                    print("Warning: concatenated_video_output is None or does not have hide_download_button.")
                return None
            
            
        concatenate_button.click(
            fn=upload_videos_and_concatenate,
            inputs=video_upload,
            outputs=concatenated_video_output
        )
       # concatenated_video_output.show_download_button("concatenated_result.mp4")
       # Handled separately in the handle function

    with gr.Tab("Saved Prompts"):
        saved_prompts_output = gr.List(label="Saved Prompts")
        load_prompts_button = gr.Button("Load Saved Prompts")
        load_prompts_button.click(fn=load_saved_prompts, outputs=saved_prompts_output)

demo.launch()