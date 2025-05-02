# agents/video_generator_agent.py
import logging
import requests
import os
from typing import Dict, Any
from utils.video_utils import concatenate_videos  # Assuming you might concatenate later
from config import GCS_BUCKET_NAME  # If you want to save generated videos to GCS
from utils.gcs_utils import upload_to_gcs  # If you want to save generated videos to GCS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with the actual base URL for the Veo API
VEO_API_BASE_URL = "YOUR_VEO_API_BASE_URL"
VEO_API_GENERATE_ENDPOINT = f"{VEO_API_BASE_URL}/generate"  # Example endpoint
VEO_API_KEY = "YOUR_VEO_API_KEY"  # Securely manage your API key

# Directory to save temporary generated videos
OUTPUT_VIDEO_DIR = "temp_generated_videos"
os.makedirs(OUTPUT_VIDEO_DIR, exist_ok=True)

class VideoGeneratorAgent:
    """
    Agent responsible for receiving text prompts and generating videos using the Veo model.
    """
    def __init__(self, veo_api_base_url=VEO_API_BASE_URL, veo_api_generate_endpoint=VEO_API_GENERATE_ENDPOINT, veo_api_key=VEO_API_KEY, output_dir=OUTPUT_VIDEO_DIR, gcs_bucket_name=GCS_BUCKET_NAME):
        """
        Initializes the VideoGeneratorAgent.

        Args:
            veo_api_base_url (str): The base URL of the Veo API.
            veo_api_generate_endpoint (str): The specific endpoint for video generation.
            veo_api_key (str): The API key for accessing the Veo API.
            output_dir (str): Directory to save temporary generated videos.
            gcs_bucket_name (str): Name of the GCS bucket to save videos (optional).
        """
        self.veo_api_base_url = veo_api_base_url
        self.veo_api_generate_endpoint = veo_api_generate_endpoint
        self.veo_api_key = veo_api_key
        self.output_dir = output_dir
        self.gcs_bucket_name = gcs_bucket_name
        logging.info(f"VideoGeneratorAgent initialized. Veo API Endpoint: {self.veo_api_generate_endpoint}, Output Directory: {self.output_dir}, GCS Bucket: {self.gcs_bucket_name}")

    def generate_video(self, prompt: str) -> Dict[str, Any]:
        """
        Generates a video based on the provided text prompt using the Veo API.

        Args:
            prompt (str): The text prompt for video generation.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the generation and
                             the path to the generated video (if successful).
        """
        logging.info(f"Received prompt for video generation: '{prompt}'")

        if not self.veo_api_key:
            error_message = "Error: Veo API key is not configured."
            logging.error(error_message)
            return {"status": "error", "message": error_message}

        headers = {
            "Authorization": f"Bearer {self.veo_api_key}",
            "Content-Type": "application/json"  # Adjust content type if needed
        }
        payload = {
            "prompt": prompt,
            # Add other parameters as required by the Veo API (e.g., duration, resolution)
        }

        try:
            logging.info(f"Sending request to Veo API: {self.veo_api_generate_endpoint} with payload: {payload}")
            response = requests.post(self.veo_api_generate_endpoint, headers=headers, json=payload, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Determine the filename for the generated video
            filename = f"veo_generated_{prompt[:20].replace(' ', '_')}_{os.urandom(4).hex()}.mp4"
            output_path = os.path.join(self.output_dir, filename)

            logging.info(f"Downloading generated video to: {output_path}")
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logging.info(f"Video generation successful. Saved at: {output_path}")
            return {"status": "success", "video_path": output_path}

        except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with Veo API: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}
        except Exception as e:
            error_message = f"An unexpected error occurred during video generation: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    # Optional: Function to handle concatenation if triggered by another agent
    def concatenate_videos_agent(self, video_paths: list) -> Dict[str, Any]:
        """
        Concatenates a list of video file paths.

        Args:
            video_paths (list): A list of paths to the video files to concatenate.

        Returns:
            Dict[str, Any]: A dictionary containing the status and the path to the
                             concatenated video (if successful).
        """
        logging.info(f"Received request to concatenate videos: {video_paths}")
        if not video_paths or len(video_paths) < 2:
            error_message = "Error: At least two video paths are required for concatenation."
            logging.error(error_message)
            return {"status": "error", "message": error_message}

        try:
            output_filename = f"concatenated_{os.urandom(4).hex()}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            concatenated_path = concatenate_videos(video_paths, output_path=output_path)
            logging.info(f"Videos concatenated successfully. Saved at: {concatenated_path}")
            return {"status": "success", "concatenated_path": concatenated_path}
        except Exception as e:
            error_message = f"Error during video concatenation: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    # Optional: Function to upload the generated video to GCS
    def upload_video_to_gcs(self, video_path: str, destination_blob_name: str = None) -> Dict[str, Any]:
        """
        Uploads the generated video to Google Cloud Storage.

        Args:
            video_path (str): The local path to the generated video file.
            destination_blob_name (str, optional): The desired name of the blob in GCS.
                                                   Defaults to the filename.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the upload and the
                             GCS URI of the uploaded video (if successful).
        """
        if not self.gcs_bucket_name:
            warning_message = "Warning: GCS bucket name is not configured. Skipping video upload."
            logging.warning(warning_message)
            return {"status": "warning", "message": warning_message}

        if not os.path.exists(video_path):
            error_message = f"Error: Video file not found at: {video_path}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

        filename = os.path.basename(video_path)
        blob_name = destination_blob_name if destination_blob_name else f"generated_videos/{filename}"

        if upload_to_gcs(self.gcs_bucket_name, video_path, blob_name):
            gcs_uri = f"gs://{self.gcs_bucket_name}/{blob_name}"
            logging.info(f"Video uploaded to GCS: {gcs_uri}")
            return {"status": "success", "gcs_uri": gcs_uri}
        else:
            error_message = f"Error uploading video {video_path} to GCS."
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    # Example of how this agent might be run or integrated
    def run(self, data: Dict[str, Any]):
        """
        Example function to process incoming data containing a prompt.

        Args:
            data (Dict[str, Any]): A dictionary containing the input data, expected to have a 'prompt' key.

        Returns:
            Dict[str, Any]: The result of the video generation process.
        """
        prompt = data.get("prompt")
        if prompt:
            return self.generate_video(prompt)
        else:
            error_message = "Error: No 'prompt' found in the input data."
            logging.error(error_message)
            return {"status": "error", "message": error_message}

if __name__ == "__main__":
    # This block is for local testing and won't be executed when deployed as a Vertex AI Agent.
    generator_agent = VideoGeneratorAgent()
    example_prompt = "A futuristic cityscape at dawn with flying vehicles."
    generation_result = generator_agent.generate_video(example_prompt)
    print(f"Generation Result: {generation_result}")

    if generation_result.get("status") == "success":
        upload_result = generator_agent.upload_video_to_gcs(generation_result["video_path"])
        print(f"GCS Upload Result: {upload_result}")

    # Example of concatenation (you'd likely get video paths from another source/agent)
    # if generation_result.get("status") == "success":
    #     concat_result = generator_agent.concatenate_videos_agent([generation_result["video_path"], "dummy_video2.mp4"]) # Replace with actual paths
    #     print(f"Concatenation Result: {concat_result}")