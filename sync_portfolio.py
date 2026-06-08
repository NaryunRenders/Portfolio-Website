import os
import re

# Configuration
PORTFOLIO_DIR = "Portfolio Pieces"
INDEX_FILE = "index.html"
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

def sync_portfolio():
    if not os.path.exists(PORTFOLIO_DIR):
        print(f"Error: {PORTFOLIO_DIR} folder not found!")
        return

    images = [f for f in os.listdir(PORTFOLIO_DIR)
              if f.lower().endswith(IMAGE_EXTENSIONS)]
    images.sort()
    print(f"Found {len(images)} images: {images}")

    if not os.path.exists(INDEX_FILE):
        print(f"Error: {INDEX_FILE} not found!")
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    new_array_str = f"const portfolioImages = {str(images)}; // SYNC_START"
    pattern = r"const portfolioImages = \[.*?\]; // SYNC_START"
    new_content = re.sub(pattern, new_array_str, content)

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Successfully synced {len(images)} portfolio images!")

if __name__ == "__main__":
    sync_portfolio()
