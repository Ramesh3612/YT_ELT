import requests
import json
import os
from datetime import date
from dotenv import load_dotenv
load_dotenv(dotenv_path='./.env')

API_KEY = os.getenv('API_KEY')

CHANNEL_HANDLE = "MrBeast"
maxResults = 50
def get_playlistId():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url)

        response.raise_for_status()

        data = response.json()
        # print(json.dumps(data, indent=4))
        channel_items = data['items'][0]
        channel_playlist = channel_items['contentDetails']['relatedPlaylists']['uploads']
        print(channel_playlist)

        return channel_playlist
    except requests.exceptions.RequestException as e:
        raise e

def get_video_ids(playlistId):
    video_ids = []
    pageToken = None
    
    Base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxresults={maxResults}&playlistId={playlistId}&key={API_KEY}&"

    
    try:
        while True:
            url = Base_url
            if pageToken:
                url += f"pageToken={pageToken}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
            pageToken = data.get('nextPageToken')
            if not pageToken:
                break
        # print(video_ids)
        return video_ids
    
    except requests.exceptions.RequestException as e:
        raise e



def extracted_video_data(video_ids):

    extracted_data = []

    def batch_list(video_ids, batch_size):
        for video in range(0, len(video_ids), batch_size):
            yield video_ids[video: video+batch_size]

    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ','.join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_data = {
                    "video_id" : video_id,
                    "title" : snippet['title'],
                    "publishedAt": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "viewCount": statistics.get('viewCount', None),
                    "likeCount": statistics.get('likeCount', None),
                    "commentCount": statistics.get('commentCount', None)

                }
                extracted_data.append(video_data)
        return extracted_data



        
    except requests.exceptions.RequestException as e:
        raise e

def save_to_json(extracted_data):
    file_path = f"./data/YT_data_{date.today()}.json"

    with open(file_path, 'w', encoding="utf-8") as output_json:
        json.dump(extracted_data, output_json, indent=4, ensure_ascii=False)

    
if __name__ == "__main__":
    playlistId = get_playlistId()
    video_ids = get_video_ids(playlistId)
    video_data =extracted_video_data(video_ids)
    save_to_json(video_data)
