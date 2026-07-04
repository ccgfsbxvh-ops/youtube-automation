"""
upload_youtube.py -- final video ko YouTube pe upload karta hai using
YouTube Data API v3, refresh token se auto re-authenticate karta hai
(one-time manual OAuth setup zaroori hai, README dekh).
"""

import json
import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import (
    VIDEO_FILE, THUMBNAIL_FILE, OUTPUT_DIR,
    YOUTUBE_CATEGORY_ID, YOUTUBE_PRIVACY_STATUS, DEFAULT_TAGS
)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "token.pickle"
CLIENT_SECRETS_FILE = "client_secret.json"  # download from Google Cloud Console


def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This branch only runs ONCE locally (first time setup).
            # On GitHub Actions this should never trigger -- token.pickle
            # must already exist and be valid/refreshable.
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_video():
    with open(f"{OUTPUT_DIR}/metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": DEFAULT_TAGS,
            "categoryId": YOUTUBE_CATEGORY_ID,
        },
        "status": {
            "privacyStatus": YOUTUBE_PRIVACY_STATUS,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(VIDEO_FILE, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"Uploaded: https://youtube.com/watch?v={video_id}")

    # set custom thumbnail
    if os.path.exists(THUMBNAIL_FILE):
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(THUMBNAIL_FILE)).execute()
        print("Thumbnail set.")

    return video_id


if __name__ == "__main__":
    upload_video()
