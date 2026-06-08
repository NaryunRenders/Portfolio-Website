# Naryun Portfolio — GitHub Pages Setup

## File Structure
```
your-repo/
├── index.html          ← main website
├── thumbnails.json     ← thumbnail data
├── videos.json         ← YouTube video data
└── images/
    ├── thumb-01.jpg
    ├── thumb-02.jpg
    └── ...
```

## How to add thumbnails

1. Export your thumbnail as a JPG/PNG (1280×720 recommended)
2. Upload it to the `images/` folder in your GitHub repo
3. Open `thumbnails.json` and add an entry:

```json
{
  "title": "Your Video Title",
  "client": "Channel Name",
  "ctr": "24% CTR",
  "image": "images/your-file.jpg"
}
```

4. Commit and push — the site updates automatically.

## How to add videos

Open `videos.json` and add an entry:

```json
{
  "title": "Video Title Here",
  "creator": "Channel Name",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "duration": "8:32",
  "views": "450K"
}
```

Paste any YouTube URL — the site extracts the video ID automatically,
fetches the thumbnail from YouTube, and plays the video inline when clicked.

## Deploy to GitHub Pages

1. Push all files to a GitHub repo
2. Go to Settings → Pages
3. Set Source to "Deploy from branch" → main → / (root)
4. Your site will be live at: https://YOUR-USERNAME.github.io/YOUR-REPO/

## Stats (in index.html)
The four counters animate up from 0 when scrolled into view.
To change the target numbers, find the `.stat-num` elements and update `data-target` and `data-suffix`.
