import requests
import json
import os

BASE_URL = "http://localhost:8000"
USERNAME = "david"
PASSWORD = "FarmWorker#2026"

print(f"Logging in as {USERNAME}...")
login_response = requests.post(f"{BASE_URL}/login", json={"username": USERNAME, "password": PASSWORD})
if login_response.status_code != 200:
    print("Login failed:", login_response.text)
    exit(1)

data = login_response.json()
token = data["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Login successful! Token acquired.")

print("\nFetching tasks to find a valid task_id...")
tasks_response = requests.get(f"{BASE_URL}/tasks", headers=headers)
tasks = tasks_response.json()
if not tasks:
    print("No tasks found to attach a voice message to.")
    exit(1)

task_id = tasks[0]["id"]
print(f"Selected Task ID: {task_id}")

print("\nCreating a dummy audio file...")
dummy_file_path = "dummy_audio.m4a"
with open(dummy_file_path, "wb") as f:
    f.write(b"dummy audio content")

print(f"\nUploading voice message to /tasks/{task_id}/voice...")
with open(dummy_file_path, "rb") as f:
    files = {"file": ("dummy_audio.m4a", f, "audio/m4a")}
    upload_response = requests.post(f"{BASE_URL}/tasks/{task_id}/voice", headers=headers, files=files)

print("Upload Response:", upload_response.status_code, upload_response.text)

print(f"\nFetching voice messages for task {task_id}...")
get_response = requests.get(f"{BASE_URL}/tasks/{task_id}/voice", headers=headers)
print("Get Response:", get_response.status_code)
print(json.dumps(get_response.json(), indent=2))

print("\nCleaning up dummy file...")
os.remove(dummy_file_path)
print("Test complete!")
