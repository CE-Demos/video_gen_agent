# agents/prompt_reader_agent.py
import logging
import requests
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the endpoint for the video generator agent
VIDEO_GENERATOR_ENDPOINT = "YOUR_VIDEO_GENERATOR_AGENT_ENDPOINT"  # Replace with the actual endpoint

class PromptReaderAgent:
    """
    Agent responsible for receiving and processing user prompts and triggering
    the video generation agent.
    """
    def __init__(self, video_generator_endpoint=VIDEO_GENERATOR_ENDPOINT):
        """
        Initializes the PromptReaderAgent.

        Args:
            video_generator_endpoint (str): The endpoint URL of the video generator agent.
        """
        self.video_generator_endpoint = video_generator_endpoint
        logging.info(f"PromptReaderAgent initialized. Video Generator Endpoint: {self.video_generator_endpoint}")

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Processes the incoming user prompt. This can include validation,
        basic pre-processing, and then triggering the video generation agent.

        Args:
            prompt (str): The text prompt provided by the user.

        Returns:
            Dict[str, Any]: A dictionary containing the processing status and potentially
                             instructions or data for the next agent.
        """
        logging.info(f"Received prompt: '{prompt}'")

        if not prompt or not prompt.strip():
            error_message = "Error: Received an empty prompt."
            logging.error(error_message)
            return {"status": "error", "message": error_message}

        if len(prompt) > 500:  # Example validation: Limit prompt length
            warning_message = "Warning: Prompt is longer than the recommended limit. It might be truncated or cause issues."
            logging.warning(warning_message)
            # Decide whether to proceed or reject long prompts
            # For now, we'll proceed
            pass

        # Trigger the video generation agent
        generation_request = {"prompt": prompt}
        logging.info(f"Sending generation request to: {self.video_generator_endpoint} with data: {generation_request}")

        try:
            response = requests.post(self.video_generator_endpoint, json=generation_request)
            response.raise_for_status()  # Raise an exception for bad status codes

            generation_result = response.json()  # Assuming the video generator returns JSON
            logging.info(f"Video generation initiated. Response: {generation_result}")
            return {"status": "processing", "message": "Prompt sent for video generation.", "generation_id": generation_result.get("generation_id")} # Include any ID for tracking

        except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with video generator agent: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    # Example of how this agent might be run or integrated (e.g., listening for HTTP requests)
    # In a Vertex AI Agent setup, you would typically define a function that gets called
    # when the agent receives an input. The 'process_prompt' method would likely be
    # this function.

if __name__ == "__main__":
    # This block is for local testing and won't be executed when deployed as a Vertex AI Agent.
    reader_agent = PromptReaderAgent()

    # Example usage:
    user_prompt = "A majestic eagle soaring over snow-capped mountains at sunset."
    result = reader_agent.process_prompt(user_prompt)
    print(f"Processing Result: {result}")

    empty_prompt_result = reader_agent.process_prompt("")
    print(f"Empty Prompt Result: {empty_prompt_result}")

    long_prompt = "This is a very long prompt that exceeds the arbitrary limit we set in the code as an example of prompt validation. It describes a detailed scene with many elements and actions unfolding over a significant amount of time, involving multiple characters and intricate environmental details, all intended to be visualized in the generated video."
    long_prompt_result = reader_agent.process_prompt(long_prompt)
    print(f"Long Prompt Result: {long_prompt_result}")