import os

DATA_DIR = "data/plants"
print(f"目錄存在: {os.path.exists(DATA_DIR)}")
print(f"目錄內容: {os.listdir(DATA_DIR)}")
