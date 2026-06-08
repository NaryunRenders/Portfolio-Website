import os
import re
import json
import urllib.request
import urllib.parse

# Configuration
PORTFOLIO_DIR = "portfolio"
INDEX_FILE    = "index.html"
VIDEOS_FILE   = "videos.txt"
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

# ─────────────────────────────────────────────
# PORTFOLIO SYNC
# ─────────────────────────────────────────────
def parse_filename(filename):
    name  = os.path.splitext(filename)[0]
    match = re.match(r'^(\d+%[_\s]?)(.*)', name)
    if match:
        ctr   = match.group(1).rstrip('_').rstrip()
        title = match.group(2).strip()
        return ctr, title
    return '', name

def sync_portfolio(content):
    if not os.path.exists(PORTFOLIO_DIR):
        print(f"Error: {PORTFOLIO_DIR} folder not found!")
        return content

    images = sorted([
        f for f in os.listdir(PORTFOLIO_DIR)
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ])
    print(f"Found {len(images)} images.")

    ctr_map = {}
    for img in images:
        ctr, _ = parse_filename(img)
        if ctr:
            ctr_map[img] = ctr + ' CTR'

    new_array = f"const portfolioImages = {str(images)}; // SYNC_START"
    content   = re.sub(r"const portfolioImages = \[.*?\]; // SYNC_START", new_array, content)

    new_ctr   = f"const portfolioCTR = {str(ctr_map)}; // CTR_SYNC"
    if re.search(r"const portfolioCTR = \{.*?\}; // CTR_SYNC", content):
        content = re.sub(r"const portfolioCTR = \{.*?\}; // CTR_SYNC", new_ctr, content)
    else:
        content = content.replace(new_array, new_array + '\n' + new_ctr)

    print(f"Portfolio synced — {len(images)} images, {len(ctr_map)} with CTR badges.")
    return content

# ─────────────────────────────────────────────
# VIDEO SYNC
# ─────────────────────────────────────────────
def extract_video_id(url):
    match = re.search(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|shorts/|embed/))([A-Za-z0-9_-]{11})', url)
    return match.group(1) if match else None

def fetch_video_meta(url):
    """Use YouTube oEmbed (no API key needed) to get title + author."""
    encoded = urllib.parse.quote(url, safe='')
    oembed_url = f"https://www.youtube.com/oembed?url={encoded}&format=json"
    try:
        with urllib.request.urlopen(oembed_url, timeout=10) as r:
            data = json.loads(r.read().decode())
            return {
                'title':   data.get('title', 'Untitled'),
                'creator': data.get('author_name', ''),
            }
    except Exception as e:
        print(f"  Warning: could not fetch metadata for {url} — {e}")
        return {'title': 'Untitled', 'creator': ''}

def fetch_duration(video_id):
    """
    Fetch duration from YouTube's no-auth page scrape.
    Falls back to '' if unavailable.
    """
    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/watch?v={video_id}",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
        # Duration appears as "lengthSeconds":"NNN" in the page data
        match = re.search(r'"lengthSeconds":"(\d+)"', html)
        if match:
            secs = int(match.group(1))
            mins, s = divmod(secs, 60)
            hrs,  m = divmod(mins, 60)
            if hrs:
                return f"{hrs}:{m:02d}:{s:02d}"
            return f"{mins}:{s:02d}"
    except Exception as e:
        print(f"  Warning: could not fetch duration for {video_id} — {e}")
    return ''

def sync_videos(content):
    if not os.path.exists(VIDEOS_FILE):
        print(f"No {VIDEOS_FILE} found, skipping video sync.")
        return content

    with open(VIDEOS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    print(f"Found {len(urls)} video URLs, fetching metadata...")

    videos = []
    for url in urls:
        vid = extract_video_id(url)
        if not vid:
            print(f"  Skipping unrecognised URL: {url}")
            continue
        print(f"  Fetching: {url}")
        meta = fetch_video_meta(url)
        meta['url']      = url
        meta['duration'] = fetch_duration(vid)
        meta['views']    = ''   # not available without API key
        videos.append(meta)
        print(f"    → {meta['title']} by {meta['creator']} ({meta['duration']})")

    new_videos = f"const videoData = {json.dumps(videos, indent=2)}; // VIDEOS_SYNC"
    if re.search(r"const videoData = \[.*?\]; // VIDEOS_SYNC", content, re.DOTALL):
        content = re.sub(r"const videoData = \[.*?\]; // VIDEOS_SYNC", new_videos, content, flags=re.DOTALL)
    else:
        # Insert after CTR_SYNC line
        content = re.sub(
            r"(const portfolioCTR = \{.*?\}; // CTR_SYNC)",
            r"\1\n" + new_videos,
            content
        )

    print(f"Videos synced — {len(videos)} entries.")
    return content

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    if not os.path.exists(INDEX_FILE):
        print(f"Error: {INDEX_FILE} not found!")
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    content = sync_portfolio(content)
    content = sync_videos(content)

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print("All done!")

if __name__ == "__main__":
    main()
