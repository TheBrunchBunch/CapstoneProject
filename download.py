import os
import gdown
FOLDER_ID = '1v2yiyaHoPmF4rzGl7ZTKmXcOMXjJxZ7p'
#save path
SAVE_DIR = './downloaded_articles'
os.makedirs(SAVE_DIR, exist_ok=True)


url = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
gdown.download_folder(
    url,
    output=SAVE_DIR,
    quiet=False,
    use_cookies=False,
    remaining_ok=True  
)

print(f" Download complete, saved to: {SAVE_DIR}")