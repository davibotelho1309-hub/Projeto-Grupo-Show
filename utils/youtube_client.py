import os
from googleapiclient.discovery import build

class YouTubeClient:
    def __init__(self):
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            raise ValueError("A variável de ambiente YOUTUBE_API_KEY não foi configurada.")
        self.youtube = build("youtube", "v3", developerKey=api_key)

    def search_videos(self, query, max_results=5):
        """Busca vídeos relacionados ao tema jurídico no YouTube."""
        request = self.youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            relevanceLanguage="pt",
            regionCode="BR"
        )
        response = request.execute()

        videos = []
        for item in response.get("items", []):
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            videos.append({"title": title, "url": url})
        return videos
