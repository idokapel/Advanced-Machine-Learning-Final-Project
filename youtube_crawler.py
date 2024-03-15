from googleapiclient.discovery import build
import pandas as pd
import re


# Load API key from a file
def load_api_key(api_key_path):
    with open(api_key_path) as f:
        api_key = f.read().strip()
    return api_key


# Convert ISO 8601 time duration to HH:MM:SS format
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

    formatted_duration = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
    return formatted_duration


# Extract data from the YouTube API response
def extract_data_from_response(response, youtube):
    data = {}
    item = response['items'][0]
    data['video_id'] = item['id']
    data['published_at'] = item['snippet'].get('publishedAt', None)
    data['title'] = item['snippet'].get('title', None)
    data['channel_id'] = item['snippet'].get('channelId', None)
    data['channel_title'] = item['snippet'].get('channelTitle', None)
    data['view_count'] = item['statistics'].get('viewCount', None)
    data['like_count'] = item['statistics'].get('likeCount', None)
    data['dislike_count'] = item['statistics'].get('dislikeCount', None)
    data['favorite_count'] = item['statistics'].get('favoriteCount', None)
    data['comment_count'] = item['statistics'].get('commentCount', None)
    data['duration'] = convert_time(item['contentDetails'].get('duration', None))
    data['definition'] = item['contentDetails'].get('definition', None)

    # Additional channel information
    channel_response = youtube.channels().list(
        part='statistics,snippet',
        id=data['channel_id']
    ).execute()

    if channel_response['items']:
        channel_info = channel_response['items'][0]
        data['subscriber_count'] = channel_info['statistics'].get('subscriberCount', None)
        data['total_channel_views'] = channel_info['statistics'].get('viewCount', None)
        data['channel_description'] = channel_info['snippet'].get('description', None)
        data['channel_published_at'] = channel_info['snippet'].get('publishedAt', None)
        data['videoCount'] = channel_info['statistics'].get('videoCount', None)  # Number of videos uploaded by the
        # channel

    data['tags'] = item['snippet'].get('tags', [])
    data['category_id'] = item['snippet'].get('categoryId', None)
    data['default_language'] = item['snippet'].get('defaultLanguage', None)
    data['default_audio_language'] = item['snippet'].get('defaultAudioLanguage', None)
    data['license'] = item['status'].get('license', None)
    data['content_rating'] = item['contentDetails'].get('contentRating', {})
    data['share_count'] = item['statistics'].get('shareCount', None)

    return data


# Fetch and return data for a set number of pages from YouTube
def get_data(api_key, query, order_by, num_of_pages=1):
    # Create an instance of the YouTube API service
    youtube = build('youtube', 'v3', developerKey=api_key)

    video_data = []
    next_page_token = None

    for page in range(num_of_pages):
        # Search for newest cooking videos
        page_request = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            maxResults=50,
            order=order_by,
            pageToken=next_page_token
        )
        page_response = page_request.execute()

        # Extract video IDs from the search results
        video_ids = [item['id']['videoId'] for item in page_response['items']]
        for video_id in video_ids:
            video_request = youtube.videos().list(
                part='snippet,statistics,contentDetails,status',
                id=video_id
            )
            video_response = video_request.execute()
            video_data.append(extract_data_from_response(video_response, youtube))

        next_page_token = page_response.get('nextPageToken')
        if not next_page_token:
            break

    return pd.DataFrame(video_data)


def main(api_key):
    df1 = get_data(api_key, num_of_pages=5, query='cooking', order_by='date')
    df2 = get_data(api_key, num_of_pages=5, query='learning', order_by='title')
    df3 = get_data(api_key, num_of_pages=5, query='travel', order_by='relevance')
    df4 = get_data(api_key, num_of_pages=5, query='technology', order_by='title')
    df = pd.concat([df1, df2, df3, df4])
    df.to_csv("youtube_dataset_new.csv", index=False)


if __name__ == '__main__':
    api_key_path = r"C:\עידו\לימודים\שנה ד\Google API Key.txt"
    api_key = load_api_key(api_key_path)
    main(api_key)
