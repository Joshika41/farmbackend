import requests
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth import create_access_token

BASE_URL = "http://localhost:8000"
MANAGER_USER = "chairman"
EMPLOYEE_USER = "david"

print(f"Generating token for {MANAGER_USER}...")
mgr_token = create_access_token(data={"sub": MANAGER_USER})

print("\nCreating a dummy audio file for instruction...")
dummy_file_path = "dummy_instruction.m4a"
with open(dummy_file_path, "wb") as f:
    f.write(b"dummy instruction content")

print(f"\nManager uploading voice instruction to {EMPLOYEE_USER}...")
with open(dummy_file_path, "rb") as f:
    upload_response = requests.post(
        f"{BASE_URL}/instructions/voice", 
        headers={"Authorization": f"Bearer {mgr_token}"}, 
        data={"recipient_username": EMPLOYEE_USER},
        files={"file": ("instruction.m4a", f, "audio/m4a")}
    )

print("Upload Response:", upload_response.status_code, upload_response.text)

print(f"\nGenerating token for Employee {EMPLOYEE_USER}...")
emp_token = create_access_token(data={"sub": EMPLOYEE_USER})

print("\nEmployee fetching voice instructions...")
get_response = requests.get(f"{BASE_URL}/instructions/voice", headers={"Authorization": f"Bearer {emp_token}"})
print("Get Response:", get_response.status_code)
print(json.dumps(get_response.json(), indent=2))

print("\nCleaning up dummy file...")
os.remove(dummy_file_path)
print("Test complete!")
