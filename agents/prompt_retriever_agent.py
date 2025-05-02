# agents/prompt_retriever_agent.py
from google.cloud import storage
from config import GCS_BUCKET_NAME
import json
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PromptRetrieverAgent:
    def __init__(self, bucket_name=GCS_BUCKET_NAME):
        """Initializes the PromptRetrieverAgent with the GCS bucket name."""
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.bucket_name)
        logging.info(f"PromptRetrieverAgent initialized for bucket: {self.bucket_name}")

    def list_saved_prompt_blobs(self, prefix="saved_prompts/"):
        """Lists all the blobs in the bucket with the given prefix."""
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            blob_names = [blob.name for blob in blobs]
            logging.info(f"Found {len(blob_names)} saved prompt blobs.")
            return blob_names
        except Exception as e:
            logging.error(f"Error listing blobs: {e}")
            return []

    def download_blob(self, blob_name, destination_file_path):
        """Downloads a blob from Google Cloud Storage to a local file."""
        try:
            blob = self.bucket.blob(blob_name)
            blob.download_to_filename(destination_file_path)
            logging.info(f"Blob {blob_name} downloaded to {destination_file_path}")
            return True
        except Exception as e:
            logging.error(f"Error downloading blob {blob_name}: {e}")
            return False

    def get_saved_prompts(self):
        """Retrieves the content of all saved prompt files from GCS."""
        saved_prompts = []
        blob_names = self.list_saved_prompt_blobs()

        for blob_name in blob_names:
            temp_file = f"temp_prompt_{blob_name.split('/')[-1]}"
            if self.download_blob(blob_name, temp_file):
                try:
                    with open(temp_file, 'r') as f:
                        data = json.load(f)
                        prompt = data.get("prompt")
                        if prompt:
                            saved_prompts.append(prompt)
                        else:
                            logging.warning(f"No 'prompt' key found in {blob_name}")
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON from {blob_name}: {e}")
                except FileNotFoundError:
                    logging.error(f"Temporary file {temp_file} not found after download.")
                finally:
                    try:
                        os.remove(temp_file)
                        logging.info(f"Temporary file {temp_file} removed.")
                    except OSError as e:
                        logging.warning(f"Error removing temporary file {temp_file}: {e}")
            else:
                logging.warning(f"Failed to download {blob_name}, skipping.")

        return saved_prompts

    # Example of how this agent might be run or integrated
    def run(self):
        """Example function to demonstrate retrieving and printing saved prompts."""
        prompts = self.get_saved_prompts()
        if prompts:
            print("--- Saved Prompts ---")
            for i, prompt in enumerate(prompts):
                print(f"{i+1}. {prompt}")
        else:
            print("No saved prompts found.")

if __name__ == "__main__":
    # This block will run only when the script is executed directly
    retriever_agent = PromptRetrieverAgent()
    retriever_agent.run()