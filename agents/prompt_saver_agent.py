# agents/prompt_saver_agent.py
from google.cloud import storage
from config import GCS_BUCKET_NAME
import json
from datetime import datetime
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PromptSaverAgent:
    def __init__(self, bucket_name=GCS_BUCKET_NAME):
        """Initializes the PromptSaverAgent with the GCS bucket name."""
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.bucket_name)
        logging.info(f"PromptSaverAgent initialized for bucket: {self.bucket_name}")

    def upload_blob(self, source_file_path, destination_blob_name):
        """Uploads a file to Google Cloud Storage."""
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(source_file_path)
            logging.info(f"File {source_file_path} uploaded to {destination_blob_name} in {self.bucket_name}.")
            return True
        except Exception as e:
            logging.error(f"Error uploading {source_file_path} to {destination_blob_name}: {e}")
            return False

    def save_prompt(self, prompt: str):
        """Saves the given prompt to Google Cloud Storage."""
        if not prompt:
            logging.warning("Received an empty prompt, nothing to save.")
            return "No prompt to save."

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"saved_prompts/prompt_{timestamp}.json"
        prompt_data = {"prompt": prompt, "saved_at": timestamp}
        temp_file_path = f"temp_prompt_{timestamp}.json"

        try:
            # Save the prompt data to a temporary local file
            with open(temp_file_path, 'w') as f:
                json.dump(prompt_data, f)
            logging.info(f"Prompt data written to temporary file: {temp_file_path}")

            # Upload the temporary file to GCS
            if self.upload_blob(temp_file_path, blob_name):
                logging.info(f"Prompt '{prompt}' saved to GCS as {blob_name}")
                return f"Prompt '{prompt}' saved to GCS."
            else:
                return f"Error uploading prompt '{prompt}' to GCS."

        except Exception as e:
            logging.error(f"An error occurred while saving prompt '{prompt}': {e}")
            return f"Error saving prompt: {e}"

        finally:
            # Clean up the temporary local file
            try:
                os.remove(temp_file_path)
                logging.info(f"Temporary file {temp_file_path} removed.")
            except OSError as e:
                logging.warning(f"Error removing temporary file {temp_file_path}: {e}")

    # Example of how this agent might be run or integrated
    def run(self, prompt_to_save: str):
        """Example function to demonstrate saving a prompt."""
        result = self.save_prompt(prompt_to_save)
        print(result)

if __name__ == "__main__":
    # This block will run only when the script is executed directly
    saver_agent = PromptSaverAgent()
    example_prompt = "Generate a video of a cat playing with a laser pointer in a sunny garden."
    saver_agent.run(example_prompt)