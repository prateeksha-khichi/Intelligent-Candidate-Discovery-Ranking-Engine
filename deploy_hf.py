import os
from huggingface_hub import HfApi, login

token = os.environ.get("HF_TOKEN")
if token:
    login(token=token)

api = HfApi()
repo_id = "prat23/candidate-ranking-dashboard"

print(f"Creating Space {repo_id}...")
try:
    api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker", exist_ok=True)
    print("Space created or already exists!")
except Exception as e:
    print(f"Failed to create space: {e}")

print("Uploading files to Space... This may take a few minutes...")
try:
    api.upload_folder(
        folder_path=".",
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=["venv/*", ".git/*", "__pycache__/*", "*.pyc"]
    )
    print("Upload complete!")
except Exception as e:
    print(f"Failed to upload files: {e}")
