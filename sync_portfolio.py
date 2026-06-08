import os
import re
import json

# Configuration
PORTFOLIO_DIR = "Portfolio Pieces"
INDEX_FILE = "index.html"
THUMBNAILS_JSON = "thumbnails.json"
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

def sync_portfolio():
    # 1. Get all images from the portfolio directory
    if not os.path.exists(PORTFOLIO_DIR):
        print(f"Error: {PORTFOLIO_DIR} folder not found!")
        return

    images = sorted([
        f for f in os.listdir(PORTFOLIO_DIR)
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ])
    print(f"Found {len(images)} images: {images}")

    # 2. Update index.html portfolioImages array
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
    print("Updated index.html portfolioImages array.")

    # 3. Sync thumbnails.json
    # Load existing entries so we preserve any CTR values already set
    existing = {}
    if os.path.exists(THUMBNAILS_JSON):
        with open(THUMBNAILS_JSON, 'r', encoding='utf-8') as f:
            try:
                for entry in json.load(f):
                    key = entry.get('image', '').split('/')[-1]
                    existing[key] = entry
            except json.JSONDecodeError:
                print("Warning: thumbnails.json was invalid, rebuilding it.")

    # Build updated list — one entry per image currently in the folder
    updated = []
    for img in images:
        if img in existing:
            # Keep the existing entry (preserves ctr, title, client)
            updated.append(existing[img])
        else:
            # New image — add a blank entry ready to be filled in
            updated.append({
                "image": img,
                "title": os.path.splitext(img)[0],
                "client": "",
                "ctr": ""
            })
        # Images that were in existing but not in `images` are simply dropped

    with open(THUMBNAILS_JSON, 'w', encoding='utf-8') as f:
        json.dump(updated, f, indent=2)

    added   = [i for i in images if i not in existing]
    removed = [k for k in existing if k not in images]
    print(f"thumbnails.json synced — {len(updated)} entries.")
    if added:   print(f"  Added:   {added}")
    if removed: print(f"  Removed: {removed}")
    print("Sync complete!")

if __name__ == "__main__":
    sync_portfolio()
