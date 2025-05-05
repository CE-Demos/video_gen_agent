# agents/prompt_reader_agent.py
import logging
from typing import Dict, Any
from agents.video_generator_agent import VideoGeneratorAgent  # Import the video generator agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PromptReaderAgent:
    """
    Agent responsible for receiving and processing user prompts and triggering
    the video generation agent directly.
    """
    def __init__(self):
        """
        Initializes the PromptReaderAgent and the VideoGeneratorAgent.
        """
        self.video_generator_agent = VideoGeneratorAgent()
        logging.info("PromptReaderAgent initialized with VideoGeneratorAgent.")

    def process_prompt(self, prompt: str, aspect_ratio: str = "16:9", allow_people: str = "dont_allow") -> Dict[str, Any]:
        """
        Processes the incoming user prompt and additional parameters, then triggers
        the video generation agent directly.

        Args:
            prompt (str): The text prompt provided by the user.
            aspect_ratio (str): The desired aspect ratio for the video ("16:9" or "9:16").
            allow_people (str): Whether to allow people in the video ("dont_allow" or "allow_adult").

        Returns:
            Dict[str, Any]: The result from the video generation agent.
        """
        logging.info(f"Received prompt: '{prompt}', Aspect Ratio: {aspect_ratio}, Allow People: {allow_people}")

        if not prompt or not prompt.strip():
            error_message = "Error: Received an empty prompt."
            logging.error(error_message)
            return {"status": "error", "message": error_message}

        # Directly call the video generation agent
        generation_result = self.video_generator_agent.generate_video(prompt, aspect_ratio, allow_people)
        return generation_result

    # Example of how this agent might be run or integrated
    # In a Vertex AI Agent setup, you would typically define a function that gets called
    # when the agent receives an input. The 'process_prompt' method would likely be
    # this function.

if __name__ == "__main__":
    # This block is for local testing
    import os
    # Ensure you have the GOOGLE_API_KEY environment variable set for the VideoGeneratorAgent
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCwtqZvVOiEx86-ZY1Xssn1sw6sikVLia0" # Replace with your actual API key for local testing

    reader_agent = PromptReaderAgent()
    user_prompt = "A majestic eagle soaring over snow-capped mountains at sunset."
    result = reader_agent.process_prompt(user_prompt)
    print(f"Processing Result: {result}")

    result_with_config = reader_agent.process_prompt(
        user_prompt, aspect_ratio="9:16", allow_people="allow_adult"
    )
    print(f"Processing Result with config: {result_with_config}")