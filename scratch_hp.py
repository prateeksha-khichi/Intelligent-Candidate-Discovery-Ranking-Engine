import json

def main():
    try:
        with open('data/processed/honeypots.json', 'r') as f:
            hps = json.load(f)
    except FileNotFoundError:
        print("honeypots.json not found.")
        return

    print(f'Total honeypots flagged: {len(hps)}')

    hp_set = set(hps)
    examples = []
    
    with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            cand = json.loads(line)
            if cand['candidate_id'] in hp_set:
                examples.append(cand)
                if len(examples) == 5:
                    break

    print("Examples:")
    for ex in examples:
        print(f"ID: {ex['candidate_id']}, Title: {ex.get('profile', {}).get('current_title', '')}")
        # Let's print some redrob_signals or reason why it might have been flagged
        # To know exactly why, we can re-evaluate the honeypot rules on this example
        from src.offline.honeypot_detector import is_honeypot
        # is_honeypot just returns bool. We can print the data that triggered it.
        skills = ex.get('skills', [])
        signals = ex.get('redrob_signals', {})
        history = ex.get('career_history', [])
        
        all_zero = True
        for k, v in signals.items():
            if isinstance(v, bool) and v is True: all_zero = False
            elif isinstance(v, (int, float)) and v > 0: all_zero = False
            
        print(f"  - Skills Count: {len(skills)}")
        print(f"  - Career Jobs: {len(history)}")
        print(f"  - All Zero Signals: {all_zero}")
        print()

if __name__ == "__main__":
    main()
