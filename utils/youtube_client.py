from googleapiclient.discovery import build
import os

class YouTubeClient:
    def __init__(self):
        api_key = os.getenv("AIzaSyASTN-AAwkkQMnpxDkzLCW4m-x8FH8n340")
        if not api_key:
            raise RuntimeError("Defina YOUTUBE_API_KEY no .env")
        self.client = build("youtube", "v3", developerKey=api_key)

    def search_videos(self, query, max_results=3):
        req = self.client.search().list(q=query, part="snippet", type="video", maxResults=max_results, order="relevance")
        res = req.execute()
        items = []
        for it in res.get("items", []):
            vid = it["id"]["videoId"]
            snip = it["snippet"]
            items.append({
                "title": snip["title"],
                "channelTitle": snip["channelTitle"],
                "publishedAt": snip["publishedAt"],
                "url": f"https://www.youtube.com/watch?v={vid}"
            })
        return items
