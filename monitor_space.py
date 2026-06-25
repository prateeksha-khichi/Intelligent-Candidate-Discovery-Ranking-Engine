import requests
import time

url = "https://huggingface.co/api/spaces/prat23/candidate-ranking-dashboard"
print("Monitoring Hugging Face Space deployment...")

while True:
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("runtime", {}).get("stage", "UNKNOWN")
            print(f"Current Status: {status}")
            
            if status == "RUNNING":
                print("✅ Deployment completed successfully! The Space is live.")
                break
            elif status == "ERROR":
                print("❌ Deployment encountered an error.")
                break
        else:
            print(f"Failed to fetch status. HTTP {resp.status_code}")
    except Exception as e:
        print(f"Error checking status: {e}")
    
    time.sleep(10)
