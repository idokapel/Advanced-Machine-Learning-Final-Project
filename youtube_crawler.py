from googleapiclient.discovery import build
from datetime import timedelta
import pandas as pd
import re

def load_api_key(api_key_path):
    with open(api_key_path) as f:
        api_key = f.read()
        return api_key


def convert_time(duration):
    hours_pattern = re.compile(r'(\d+)H')
    minutes_pattern = re.compile(r'(\d+)M')
    seconds_pattern = re.compile(r'(\d+)S')

    hours = hours_pattern.search(duration)
    minutes = minutes_pattern.search(duration)
    seconds = seconds_pattern.search(duration)

    hours = int(hours.group(1)) if hours else 0
    minutes = int(minutes.group(1)) if minutes else 0
    seconds = int(seconds.group(1)) if seconds else 0

    # Format the duration as "HH:MM:SS"
    formatted_duration = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)

    return formatted_duration


def extract_data_from_response(response):
    data = {}
    item = response['items'][0]
    data['video_id'] = item['id']
    data['published_at'] = item['snippet']['publishedAt']
    data['title'] = item['snippet']['title']
    data['channel_title'] = item['snippet']['channelTitle']
    data['view_count'] = item['statistics']['viewCount']
    data['like_count'] = item['statistics']['likeCount']
    data['favorite_count'] = item['statistics']['favoriteCount']
    data['comment_count'] = item['statistics']['commentCount']
    data['duration'] = convert_time(item['contentDetails']['duration'])
    data['definition'] = item['contentDetails']['definition']
    return data


def get_data(api_key, num_of_videos=1):
    # Create an instance of YouTube service
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Search for trending videos
    request = youtube.search().list(
        part='snippet',
        q='trending',
        type='video',
        videoDuration='short',  # Optional: filter for short videos
        maxResults=num_of_videos
    )
    response = request.execute()

    # Extract video IDs from the search results
    video_ids = [item['id']['videoId'] for item in response['items']]
    video_data = []

    for video_id in video_ids:
        request = youtube.videos().list(
            part='snippet, statistics, contentDetails',
            id=video_id
        )
        video_response = request.execute()
        video_data.append(extract_data_from_response(video_response))

    # Create pandas DataFrame from the collected data
    df = pd.DataFrame(video_data)
    return df


if __name__ == '__main__':
    api_key_path = r"C:\עידו\לימודים\שנה ד\Google API Key.txt"
    api_key = load_api_key(api_key_path)
    df = get_data(api_key, num_of_videos=1)
    # df.to_csv("youtube_dataset.csv")
