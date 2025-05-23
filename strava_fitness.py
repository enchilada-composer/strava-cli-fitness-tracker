import os
import requests
import json
from datetime import datetime, timedelta
import dotenv
from dotenv import load_dotenv, set_key

class StravaFitnessAnalyzer:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.access_token = os.getenv('STRAVA_ACCESS_TOKEN')
        self.base_url = "https://www.strava.com/api/v3"

    def save_access_token(self, token):
        """Save access token to .env file"""
        set_key('.env', 'STRAVA_ACCESS_TOKEN', token)
        print("Access token saved to .env file")

    def get_access_token(self, auth_code):
        """Get access token using authorization code"""
        if not self.client_id or not self.client_secret:
            print("Error: Missing Strava credentials. Please check your .env file.")
            print("You need to set both STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET")
            return None

        url = f"{self.base_url}/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            token = response.json()['access_token']
            self.access_token = token
            self.save_access_token(token)
            print("Successfully obtained access token!")
            return token
        else:
            error_msg = response.json().get('message', 'Unknown error')
            print(f"Error getting access token: {error_msg}")
            return None

    def get_activities(self, days=30):
        """Get activities from the last X days"""
        if not self.access_token:
            print("No access token available. Please authorize first.")
            print("Visit: https://www.strava.com/oauth/authorize?client_id={}&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all".format(self.client_id))
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
        total_elevation_gain = 0
        
        for activity in activities:
            total_distance += activity.get('distance', 0)
            total_time += activity.get('moving_time', 0)
            total_elevation_gain += activity.get('total_elevation_gain', 0)

        # Convert to more readable units
        total_distance_km = total_distance / 1000
        total_time_hours = total_time / 3600
        
        # Calculate weekly training load
        weekly_distance = total_distance_km
        weekly_hours = total_time_hours
        weekly_elevation = total_elevation_gain
        
        # Calculate fitness metrics
        avg_distance = weekly_distance / len(activities) if activities else 0
        avg_time = weekly_hours / len(activities) if activities else 0
        avg_elevation = weekly_elevation / len(activities) if activities else 0
        
        # Calculate training load
        training_load = weekly_distance * avg_time
        
        # Determine fitness status
        fitness_status = ""
        if training_load > 100:  # High training load
            if avg_time > 2:  # Long duration workouts
                fitness_status = "Fatigued - Consider reducing intensity"
            else:
                fitness_status = "Fit - Maintaining high training load"
        elif training_load > 50:  # Moderate training load
            if avg_time > 1.5:
                fitness_status = "Ready - Good balance of volume and intensity"
            else:
                fitness_status = "Fit - Building endurance"
        else:  # Low training load
            if avg_time > 1:
                fitness_status = "Ready - Good recovery phase"
            else:
                fitness_status = "Fit - Maintaining base fitness"

        print("\n=== Weekly Fitness Summary ===")
        print(f"Total Distance: {total_distance_km:.2f} km")
        print(f"Total Time: {total_time_hours:.2f} hours")
        print(f"Total Elevation Gain: {weekly_elevation:.2f} m")
        print(f"Training Load: {training_load:.2f}")
        print(f"\nFitness Status: {fitness_status}")
        
        # Calculate average metrics
        if activities:
            print("\n=== Average Per Activity ===")
            print(f"Average Distance: {avg_distance:.2f} km")
            print(f"Average Time: {avg_time:.2f} hours")
            print(f"Average Elevation Gain: {avg_elevation:.2f} m")

if __name__ == "__main__":
    analyzer = StravaFitnessAnalyzer()
    
    # Check if we have an access token
    if not analyzer.access_token:
        print("\nPlease authorize the application:")
        print("Visit this URL in your browser:")
        print(f"https://www.strava.com/oauth/authorize?client_id={analyzer.client_id}&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all")
        print("\nAfter authorizing, you'll be redirected to localhost with a URL like:")
        print("http://localhost/?state=&code=YOUR_AUTH_CODE&scope=read,activity:read_all")
        print("\nCopy the code parameter (the long string after 'code=') and paste it here:")
        
        try:
            auth_code = input("Authorization code: ")
            if analyzer.get_access_token(auth_code):
                print("\nSuccessfully obtained access token!")
                print("The token has been saved to your .env file. You won't need to authorize again unless the token expires.")
            else:
                print("Failed to obtain access token. Please try again.")
                exit(1)
        except EOFError:
            print("\nAuthorization cancelled. Exiting.")
            exit(1)
    
    # Get and analyze activities
    activities = analyzer.get_activities(days=7)
    if activities:
        analyzer.analyze_fitness(activities)
    else:
        print("\nNo activities found. Make sure your access token is valid and you have activities in your Strava account.")
