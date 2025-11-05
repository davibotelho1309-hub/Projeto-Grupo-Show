import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def buscar_videos_youtube(tema: str, max_results=3):
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("A variável YOUTUBE_API_KEY não foi configurada.")
    
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        part="snippet",
        q=f"{tema} direito STF explicação",
        type="video",
        maxResults=max_results,
        relevanceLanguage="pt"
    )
    response = request.execute()

    videos = []
    for item in response["items"]:
        videos.append({
            "titulo": item["snippet"]["title"],
            "canal": item["snippet"]["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        })
    return videos
