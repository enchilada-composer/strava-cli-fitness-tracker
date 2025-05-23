import os
import requests
import json
from datetime import datetime, timedelta
import dotenv

class StravaFitnessAnalyzer:
    def __init__(self):
        dotenv.load_dotenv()
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.access_token = None
        self.base_url = "https://www.strava.com/api/v3"

    def get_access_token(self, auth_code):
        """Get access token using authorization code"""
        url = f"{self.base_url}/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
            return self.access_token
        else:
            print(f"Error getting access token: {response.text}")
            return None

    def get_activities(self, days=30):
        """Get activities from the last X days"""
        if not self.access_token:
            print("No access token available. Please authorize first.")
            return []

        url = f"{self.base_url}/athlete/activities"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {
            'per_page': 200,
            'page': 1,
            'after': int((datetime.now() - timedelta(days=days)).timestamp())
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching activities: {response.text}")
            return []

    def analyze_fitness(self, activities):
        """Analyze fitness metrics from activities"""
        if not activities:
            print("No activities found. Make sure your access token is valid.")
            return

        total_distance = 0
        total_time = 0
        total_elevation = 0
        
        for activity in activities:
            total_distance += activity.get('distance', 0)
            total_time += activity.get('moving_time', 0)
            total_elevation += activity.get('total_elevation_gain', 0)

        # Convert to more readable units
        total_distance_km = total_distance / 1000
        total_time_hours = total_time / 3600
        
        print("\n=== Weekly Fitness Summary ===")
        print(f"Total Distance: {total_distance_km:.2f} km")
        print(f"Total Time: {total_time_hours:.2f} hours")
        print(f"Total Elevation Gain: {total_elevation:.2f} m")
        
        # Calculate average metrics
        if activities:
            avg_distance = total_distance_km / len(activities)
            avg_time = total_time_hours / len(activities)
            print("\n=== Average Per Activity ===")
            print(f"Average Distance: {avg_distance:.2f} km")
            print(f"Average Time: {avg_time:.2f} hours")

if __name__ == "__main__":
    analyzer = StravaFitnessAnalyzer()
    
    # Get access token if not already set
    if not analyzer.access_token:
        print("\nPlease authorize the application first:")
        print("Visit: https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all")
        print("\nAfter authorizing, enter the authorization code from the URL:")
        auth_code = input("Authorization code: ")
        analyzer.get_access_token(auth_code)
    
    # Get and analyze activities
    activities = analyzer.get_activities(days=7)
    analyzer.analyze_fitness(activities)
