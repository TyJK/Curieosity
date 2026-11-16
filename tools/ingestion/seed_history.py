import os

LOG_DIR = "./tools/logs"
HISTORY_FILE = os.path.join(LOG_DIR, "processed_datasets.txt")

# The 22 files confirmed processed in your previous 8-hour run
DONE_LIST = [
    "ord_dataset-00005539a1e04c809a9a78647bea649c.pb.gz",
    "ord_dataset-018fd0e1351f4fd09b20fcddd97b4c7a.pb.gz",
    "ord_dataset-01dbb772c5e249108f0b191ed17a2c0c.pb.gz",
    "ord_dataset-02ee2261663048188cf6d85d2cc96e3f.pb.gz",
    "ord_dataset-0316886541d9435489859c2ad7edc863.pb.gz",
    "ord_dataset-0387783899c642a8b7eb4ba379bcdf5d.pb.gz",
    "ord_dataset-03ba810b7f464a06b5d8787af2e8b64e.pb.gz",
    "ord_dataset-04982f13ed08448d93df6794846500f3.pb.gz",
    "ord_dataset-04d607efe1d9485eb99fafa06880f62e.pb.gz",
    "ord_dataset-053897d9b1744303b2fdfe3e796ca27b.pb.gz",
    "ord_dataset-06d4002fc4d34860a0688cba690e12dc.pb.gz",
    "ord_dataset-074f86301ec5441ab3b52d902ac06949.pb.gz",
    "ord_dataset-07db50a3ce6941919df30a9e2898988f.pb.gz",
    "ord_dataset-081613ef79bd4110aacc146b4465f086.pb.gz",
    "ord_dataset-08852243bba44cb28769a5833f1515fe.pb.gz",
    "ord_dataset-09e9a37ee5794dc28c0ad7bf7a442c18.pb.gz",
    "ord_dataset-0a66204fc43e49c2922e6f9107e6b62f.pb.gz",
    "ord_dataset-0b24d1f58a024ed7bc2bda95b2430c72.pb.gz",
    "ord_dataset-0b32b90cc77b4a3db47ad263e0bbc1a8.pb.gz",
    "ord_dataset-0b70410902ae4139bd5d334881938f69.pb.gz",
    "ord_dataset-0bb2e99daa66408fb8dbd6a0781d241c.pb.gz",
    "ord_dataset-0bf72e95d80743729fdbb8b57a4bc0c6.pb.gz"
]

def seed():
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        for filename in DONE_LIST:
            f.write(f"{filename}\n")

    print(f"✅ Successfully seeded {len(DONE_LIST)} datasets into history.")
    print(f"📄 Location: {HISTORY_FILE}")

if __name__ == "__main__":
    seed()