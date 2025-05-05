# config.py
import os

# Google Cloud Storage Settings
GCS_BUCKET_NAME = "veo_exps"  # Replace with your bucket name

# API Keys (Consider using environment variables for security)
VEO_API_KEY = os.environ.get("VEO_API_KEY")
# GRADIO_API_KEY = os.environ.get("GRADIO_API_KEY")

# Other configurations as needed