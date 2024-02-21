from googleapiclient.discovery import build
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
    data['published_at'] = item['snippet'].get('publishedAt', None)
    data['title'] = item['snippet'].get('title', None)
    data['channel_title'] = item['snippet'].get('channelTitle', None)
    data['view_count'] = item['statistics'].get('viewCount', None)
    data['like_count'] = item['statistics'].get('likeCount', None)
    data['favorite_count'] = item['statistics'].get('favoriteCount', None)
    data['comment_count'] = item['statistics'].get('commentCount', None)
    data['duration'] = convert_time(item['contentDetails'].get('duration', None))
    data['definition'] = item['contentDetails'].get('definition', None)
    return data


def get_data(api_key, num_of_pages=1):
    # Create an instance of YouTube service
    youtube = build('youtube', 'v3', developerKey=api_key)

    video_data = []
    next_page_token = None
    page_counter = 0

    while True:
        # Search for trending videos
        page_request = youtube.search().list(
            part='snippet',
            q='trending',
            type='video',
            maxResults=50,
            pageToken=next_page_token  # Initialize pageToken for first request
        )
        page_counter += 1  # Count the number of pages
        page_response = page_request.execute()

        # Extract video IDs from the search results
        video_ids = [item['id']['videoId'] for item in page_response['items']]

        for video_id in video_ids:
            video_request = youtube.videos().list(
                part='snippet, statistics, contentDetails',
                id=video_id
            )
            video_response = video_request.execute()
            video_data.append(extract_data_from_response(video_response))

        # Update next_page_token for next iteration
        next_page_token = page_response.get('nextPageToken')

        # If there isn't a next page, or got to max pages desired, break the loop
        if (not next_page_token) or (page_counter == num_of_pages):
            break

    # Create pandas DataFrame from the collected data
    df = pd.DataFrame(video_data)
    return df


if __name__ == '__main__':
    api_key_path = r"C:\עידו\לימודים\שנה ד\Google API Key.txt"
    api_key = load_api_key(api_key_path)
    df = get_data(api_key, num_of_pages=10)
    df.to_csv("youtube_dataset.csv")
