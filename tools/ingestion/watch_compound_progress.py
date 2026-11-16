import os
import time
import sys

DATA_DIR = "./tools/data/reaction_dataset"

def watch():
    print(f"👀 Watching {DATA_DIR}...")
    print("Ctl+C to stop watching (won't stop ingestion).")
    print("-" * 40)

    start_count = len([n for n in os.listdir(DATA_DIR) if n.endswith('.json')])
    start_time = time.time()

    while True:
        current_count = len([n for n in os.listdir(DATA_DIR) if n.endswith('.json')])
        elapsed = time.time() - start_time

        new_files = current_count - start_count
        rate = new_files / elapsed if elapsed > 0 else 0

        sys.stdout.write(f"\r🚀 Total Reactions: {current_count:,}  |  Session New: +{new_files}  |  Speed: {rate:.1f} rxns/sec")
        sys.stdout.flush()
        time.sleep(2)

if __name__ == "__main__":
    watch()