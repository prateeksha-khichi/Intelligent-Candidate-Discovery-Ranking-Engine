import json
rule3_count = 0
empty_signals = 0
all_zero_count = 0

with open('data/raw/candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        cand = json.loads(line)
        signals = cand.get('redrob_signals', {})
        if not signals:
            empty_signals += 1
            continue
            
        all_zero = True
        for k, v in signals.items():
            if isinstance(v, bool) and v is True: all_zero = False
            elif isinstance(v, (int, float)) and v > 0: all_zero = False
            elif isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, (int, float)) and sub_v > 0: all_zero = False
        
        if all_zero:
            all_zero_count += 1

print(f'Empty signals: {empty_signals}, All zero signals: {all_zero_count}')
