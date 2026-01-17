import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from google import genai
from pydantic import BaseModel, Field
from typing import List

# Spotify and Gemini setup are in functions so that server.py can call them 

### SPOTIFY API SETUP ###
def get_spotify_account(user_name):
    CLIENT_ID = "[Enter Spotify Client ID]"
    CLIENT_SECRET = "Enter Spotify Client Secret"
    REDIRECT_URI = "Enter Redirect Uri"

    client_manager = spotipy.SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    auth_manager = SpotifyOAuth(
        client_id= CLIENT_ID,
        client_secret= CLIENT_SECRET,
        redirect_uri= REDIRECT_URI,
        scope= "playlist-read-private playlist-read-collaborative"
    )
    spotify = spotipy.Spotify(client_credentials_manager=client_manager, auth_manager=auth_manager)

    playlists = spotify.user_playlists(user_name, limit=2) ### limit
    all_playlists = {}

    # Store song (title: artist) from all user playlists in 'all_playlists' dictionary
    for playlist in playlists["items"]:
        playlist_id = playlist["id"]
        playlist_songs = spotify.playlist_items(playlist_id, limit=2) ### limit

        song_name = playlist_songs["items"][0]["track"]["name"]
        artist_name = playlist_songs["items"][0]["track"]["artists"][0]["name"]

        all_playlists[playlist["name"]] = {
            song_name: artist_name
        }

    return all_playlists

### GEMINI API SETUP ###
def gemini_roast(user_playlists):

    class Paragraphs(BaseModel):
        header: str = Field(description="Title of paragraph")
        content: str = Field(description="Paragraph discussing your opinion of an aspect/song/playlist in the user's spotify")

    class Generate_Roast(BaseModel): # allows Gemini to return response in JSON format 
        intro: str = Field(description="Introductory statement on your initial opinion of the user's spotify")
        all_paragraphs : List[Paragraphs]
        verdict: str = Field(description="'The Verdict' with your overall opinion and a closing statement")

    api_key = "[Insert Gemini API Key]"
    client = genai.Client(api_key=api_key)

    prompt = f"Can you roast me based on the songs and playlists in my Spotify? \
               You don't have to do every playlist, but give me your overall opinion. \
               Try to keep it around 400 words. Here are my playlists and songs: {user_playlists}"

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": Generate_Roast.model_json_schema(),
        },
    )

    roast_response = Generate_Roast.model_validate_json(response.text)

    return roast_response # in JSON format



