import os
import requests
import json
from datetime import datetime, timedelta
import dotenv
from dotenv import load_dotenv, set_key
import re
import time

class StravaFitnessAnalyzer:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.access_token = os.getenv('STRAVA_ACCESS_TOKEN')
        self.refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
        self.expires_at = int(os.getenv('STRAVA_EXPIRES_AT', '0'))
        self.base_url = "https://www.strava.com/api/v3"
        
        # Check if token is about to expire and refresh it if needed
        if self.refresh_token and self.access_token and self.expires_at:
            if time.time() > self.expires_at - 300:  # Refresh 5 minutes before expiration
                self.refresh_access_token()

    def save_access_token(self, token):
        """Save access token to .env file"""
        try:
            # Load existing .env content
            with open('.env', 'r') as f:
                content = f.read()
            
            # Update the token
            content = re.sub(r'STRAVA_ACCESS_TOKEN=[^\n]*', f'STRAVA_ACCESS_TOKEN={token}', content)
            
            # Write back to file
            with open('.env', 'w') as f:
                f.write(content)
            
            print("Access token saved to .env file")
        except Exception as e:
            print(f"Error saving access token: {str(e)}")
            return False
        return True

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
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                token_data = response.json()
                print(f"Token data received: {token_data}")
                
                # Save all token data to .env
                with open('.env', 'r') as f:
                    content = f.read()
                    
                # Update access token
                content = re.sub(r'STRAVA_ACCESS_TOKEN=[^\n]*', 
                              f'STRAVA_ACCESS_TOKEN={token_data["access_token"]}', 
                              content)
                              
                # Add refresh token if present
                if "refresh_token" in token_data:
                    content = re.sub(r'STRAVA_REFRESH_TOKEN=[^\n]*', 
                                  f'STRAVA_REFRESH_TOKEN={token_data["refresh_token"]}', 
                                  content, flags=re.IGNORECASE)
                    
                # Add expires_at if present
                if "expires_at" in token_data:
                    content = re.sub(r'STRAVA_EXPIRES_AT=[^\n]*', 
                                  f'STRAVA_EXPIRES_AT={token_data["expires_at"]}', 
                                  content, flags=re.IGNORECASE)
                    
                # Add expires_in if present
                if "expires_in" in token_data:
                    content = re.sub(r'STRAVA_EXPIRES_IN=[^\n]*', 
                                  f'STRAVA_EXPIRES_IN={token_data["expires_in"]}', 
                                  content, flags=re.IGNORECASE)
                    
                # If expires_at is not present but expires_in is, calculate it
                if "expires_in" in token_data and "expires_at" not in token_data:
                    expires_at = int(time.time()) + token_data["expires_in"]
                    content = re.sub(r'STRAVA_EXPIRES_AT=[^\n]*', 
                                  f'STRAVA_EXPIRES_AT={expires_at}', 
                                  content, flags=re.IGNORECASE)
                    
                with open('.env', 'w') as f:
                    f.write(content)
                    
                self.access_token = token_data["access_token"]
                self.refresh_token = token_data.get("refresh_token")
                self.expires_at = token_data.get("expires_at", 0)
                print("Successfully obtained access token!")
                print(f"Token will expire in {token_data.get('expires_in', 'unknown')} seconds")
                return token_data["access_token"]
            else:
                error_msg = response.json().get('message', 'Unknown error')
                print(f"Error getting access token: {error_msg}")
                print(f"Full response: {response.text}")
                return None
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return None

    def refresh_access_token(self):
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            print("No refresh token available. Please authorize first.")
            return False

        url = f"{self.base_url}/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                token_data = response.json()
                print("Successfully refreshed access token!")
                
                # Update token data
                self.access_token = token_data["access_token"]
                self.refresh_token = token_data.get("refresh_token", self.refresh_token)
                self.expires_at = token_data.get("expires_at", 0)
                
                # Save to .env
                with open('.env', 'r') as f:
                    content = f.read()
                    
                content = re.sub(r'STRAVA_ACCESS_TOKEN=[^\n]*', 
                              f'STRAVA_ACCESS_TOKEN={token_data["access_token"]}', 
                              content)
                
                if "refresh_token" in token_data:
                    content = re.sub(r'STRAVA_REFRESH_TOKEN=[^\n]*', 
                                  f'STRAVA_REFRESH_TOKEN={token_data["refresh_token"]}', 
                                  content, flags=re.IGNORECASE)
                    
                content = re.sub(r'STRAVA_EXPIRES_AT=[^\n]*', 
                              f'STRAVA_EXPIRES_AT={token_data.get("expires_at", 0)}', 
                              content, flags=re.IGNORECASE)
                    
                with open('.env', 'w') as f:
                    f.write(content)
                    
                print(f"Token will expire in {token_data.get('expires_in', 'unknown')} seconds")
                return True
            else:
                error_msg = response.json().get('message', 'Unknown error')
                print(f"Error refreshing token: {error_msg}")
                print(f"Full response: {response.text}")
                return False
        except Exception as e:
            print(f"Exception occurred while refreshing token: {str(e)}")
            return False

    def get_activities(self, days=30):
        """Get activities from the last X days"""
        # Check if token is valid
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
    
    # Try to get activities first - this will automatically refresh token if needed
    activities = analyzer.get_activities(days=7)
    
    if activities:
        analyzer.analyze_fitness(activities)
    else:
        # If we have no activities and no token, ask for authorization
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
                    
                    # Try to get activities again
                    activities = analyzer.get_activities(days=7)
                    if activities:
                        analyzer.analyze_fitness(activities)
                    else:
                        print("\nNo activities found. Make sure you have activities in your Strava account.")
                else:
                    print("Failed to obtain access token. Please try again.")
                    exit(1)
            except EOFError:
                print("\nAuthorization cancelled. Exiting.")
                exit(1)
        else:
            print("\nNo activities found. Make sure you have activities in your Strava account.")
