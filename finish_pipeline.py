import subprocess
import time
import psutil
import csv
import sys
import os

def run_cmd(cmd):
    print(f"==========================================")
    print(f"Running: {' '.join(cmd)}")
    print(f"==========================================")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(1)

def measure_rank_candidates():
    print(f"==========================================")
    print(f"Running: python -m src.ranking.rank_candidates")
    print(f"==========================================")
    start_time = time.time()
    
    # Adding current directory to PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(".")
    
    process = subprocess.Popen(["python", "-m", "src.ranking.rank_candidates"], env=env)
    
    peak_ram = 0
    while process.poll() is None:
        try:
            p = psutil.Process(process.pid)
            mem = p.memory_info().rss
            if mem > peak_ram:
                peak_ram = mem
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        time.sleep(0.5)
        
    end_time = time.time()
    duration = end_time - start_time
    
    if process.returncode != 0:
        print(f"rank_candidates.py failed with exit code {process.returncode}")
        sys.exit(1)
        
    return duration, peak_ram / (1024 * 1024)

def count_honeypots():
    import json
    honeypot_ids = set()
    from src.offline.honeypot_detector import is_honeypot
    print("Pre-loading all honeypot IDs for checking...")
    with open("data/raw/candidates.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            if is_honeypot(c):
                honeypot_ids.add(c["candidate_id"])
                
    hp_count = 0
    with open("outputs/submission.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 100: break
            if row["candidate_id"] in honeypot_ids:
                hp_count += 1
    return hp_count

def get_top_20():
    rows = []
    with open("outputs/submission.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i <= 20:
                rows.append(",".join(row))
    return "\n".join(rows)

def main():
    try:
        # We skip build_embeddings and build_faiss_index as they already succeeded.
        duration, peak_ram = measure_rank_candidates()
        
        print(f"\n--- rank_candidates.py Stats ---")
        print(f"Execution Time: {duration:.2f} seconds")
        print(f"Peak RAM Usage: {peak_ram:.2f} MB")
        
        print("\n--- validate_submission.py Output ---")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath(".")
        subprocess.run(["python", "validate_submission.py"], env=env)
        
        hp_count = count_honeypots()
        print(f"\n--- Honeypot Count in Top 100 ---")
        print(f"Count: {hp_count}")
        
        print("\n--- Top 20 Rows ---")
        print(get_top_20())
        
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
