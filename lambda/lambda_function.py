import json
import subprocess
import time
import threading
import requests
import ollama

ollama_process = None


def log_process_output(process):
    for line in iter(process.stdout.readline, ""):
        print(f"Ollama stdout: {line.strip()}")
    for line in iter(process.stderr.readline, ""):
        print(f"Ollama stderr: {line.strip()}")


def check_ollama_running():
    global ollama_process
    if ollama_process:
        return_code = ollama_process.poll()
        if return_code is not None:
            print(f"Ollama process exited with return code {return_code}")
            ollama_process = None
        else:
            print("Ollama process is still running")

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
        ["ollama", "serve"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    # Start a thread to continuously read and log the process output
    log_thread = threading.Thread(target=log_process_output, args=(ollama_process,))
    log_thread.daemon = True
    log_thread.start()

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
        response = ollama.generate(model="gemma:7b", prompt=prompt)
        return response["response"]
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
