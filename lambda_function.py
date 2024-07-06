import json
import subprocess
import time
import requests

ollama_process = None


def check_ollama_running():
    try:
        response = requests.get("http://localhost:11434", timeout=5)
        return response.text == "Ollama is running"
    except requests.RequestException:
        return False


def start_ollama():
    global ollama_process
    if check_ollama_running():
        print("Ollama is already running")
        return True

    print("Starting Ollama server...")
    ollama_process = subprocess.Popen(
        ["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Wait for Ollama to start
    start_time = time.time()
    while time.time() - start_time < 60:  # Wait up to 60 seconds
        if check_ollama_running():
            print("Ollama server is ready")
            return True
        time.sleep(1)
    print("Ollama server failed to become ready")
    return False


def query_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma:7b", "prompt": prompt, "stream": False},
            timeout=300,
        )
        return response.json()
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return {"error": str(e)}


def lambda_handler(event, context):
    if not check_ollama_running():
        if not start_ollama():
            return {
                "statusCode": 500,
                "body": json.dumps("Failed to start Ollama server"),
            }

    try:
        body = json.loads(event["body"])
        prompt = body.get("prompt", "")
        result = query_ollama(prompt)

        return {"statusCode": 200, "body": json.dumps(result)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}
