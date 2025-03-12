import os
import csv
import pandas as pd
from googleapiclient.discovery import build
import isodate

# Define your YouTube API key here
API_KEY = 'Your Key'

# Initialize the YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_categories(region_code='SG'):
    categories = {}
    try:
        # Request video categories for the specified region
        request = youtube.videoCategories().list(
            part="snippet",
            regionCode=region_code
        )
        response = request.execute()

        # Map categoryId to category title
        for item in response['items']:
            categories[item['id']] = item['snippet']['title']

        return categories
    except Exception as e:
        print(f"An error occurred while fetching video categories: {e}")
        return {}

def get_most_popular_videos(region_code='SG', max_results=100):
    videos = []
    next_page_token = None

    while True:
        try:
            # Request the most popular videos for the specified region
            request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                chart="mostPopular",
                regionCode=region_code,  # Change to any country code like 'IN', 'GB', 'US'
                maxResults=100,  # Maximum number of videos per request (max: 50)
                pageToken=next_page_token  # For pagination (nextPageToken)
            )
            response = request.execute()

            # Extract video details from the response
            for item in response['items']:
                video_details = {
                    #'title': item['snippet']['title'],
                    #'description': item['snippet']['description'],
                    'duration': item['contentDetails']['duration'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'video_id': item['id'],
                    'category_id': item['snippet'].get('categoryId', 'N/A'),
                    'views': item['statistics'].get('viewCount', 'N/A'),
                    'likes': item['statistics'].get('likeCount', 'N/A'),
                    #'dislikes': item['statistics'].get('dislikeCount', 'N/A',),
                }
                videos.append(video_details)

            # If a nextPageToken is returned, keep fetching the next page of results
            next_page_token = response.get('nextPageToken')
            if not next_page_token or len(videos) >= max_results:
                break  # Stop if there are no more pages or we've reached max_results

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return videos

def convert_to_dataframe(videos, categories):
    # Convert the list of video data to a pandas DataFrame
    df = pd.DataFrame(videos)

    # Map categoryId to category title
    df['category'] = df['category_id'].map(categories)

    # If you want to add a 'Video URL' column based on the video_id
 #   df['Video URL'] = 'https://www.youtube.com/watch?v=' + df['video_id']
    
    return df

def export_to_csv(df, filename='popular_videos.csv'):
    try:
        # Export the DataFrame to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data has been successfully exported to {filename}")
    except Exception as e:
        print(f"An error occurred while exporting data to CSV: {e}")

def iso8601_to_seconds(duration):
    # Parse the ISO 8601 duration string to a timedelta object
    td = isodate.parse_duration(duration)
    
    # Return the total duration in seconds
    return td.total_seconds()

def main():
    # Get the top 20 most popular videos in the US (can be changed to other regions like 'IN', 'GB', etc.)
    region_code = 'SG'  # Change this to get popular videos from another region
    max_results = 100  # Set the number of videos you want to fetch
    print(f"Fetching most popular videos in {region_code}...")

    # Step 1: Fetch video categories
    categories = get_video_categories(region_code)

    # Step 2: Fetch popular videos
    popular_videos = get_most_popular_videos(region_code, max_results)

    # Step 3: Convert the results into a DataFrame
    df = convert_to_dataframe(popular_videos, categories)

    # Display the DataFrame (optional)
    pd.set_option('display.max_columns', None)


    # Convert iso duration to sec
   # iso_duration = df[:]['duration'] # 1 hour, 30 minutes, and 15 seconds
  #  seconds = iso8601_to_seconds(iso_duration)
    #print(f"The duration in seconds is: {seconds}")

    # Show the columns 
 
    display(df.sort_values("views",ascending=False).head(10))

    display(df.groupby(["category"]).size())
    
    # Step 4: Export the results to a CSV file
    export_to_csv(df, 'popular_videos.csv')

if __name__ == '__main__':
    main()
