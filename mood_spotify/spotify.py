import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# Set your Spotify credentials
SPOTIFY_CLIENT_ID = "890a8d0563584678982d9a83e3de85f5"
SPOTIFY_CLIENT_SECRET = "626c2a2fd2e841958fa5161ddf01b1bf"

# Authenticate
auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)


def get_playlists_by_mood(mood, limit=5):
    fallback_moods = {
        "joy": "happy",
        "sadness": "sad",
        "anger": "angry",
        "fear": "calm",
        "love": "romantic",
        "neutral": "chill",
        "trauma": "healing",
        "disgust": "lighthearted",
        "surprise": "celebration"
    }

    search_term = fallback_moods.get(mood.lower(), mood.lower())
    query = f"{search_term} playlist"

    try:
        results = sp.search(q=query, type="playlist", limit=limit)

        if not results or "playlists" not in results:
            print(f"[Spotify] No results for query: {query}")
            return []

        items = results["playlists"].get("items", [])
        playlists = []
        for item in items:
            if not item or not isinstance(item, dict):  # <- ✅ Check item is valid dict
                continue

            name = item.get("name")
            url = item.get("external_urls", {}).get("spotify")

            # SAFELY get image
            images = item.get("images") or []
            if len(images) > 0 and images[0].get("url"):
                image = images[0]["url"]
            else:
                image = "https://via.placeholder.com/64"

            if name and url:
                playlists.append({
                    "name": name,
                    "url": url,
                    "image": image
                })
        print(f"[Spotify] Found {len(playlists)} playlists for mood '{mood}' → query: '{query}'")   
        return playlists

    except Exception as e:
        print("⚠️ Spotify API error:", e)
        return []

