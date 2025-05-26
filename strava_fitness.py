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
        
        # Try to refresh token if we have one
        if self.refresh_token:
            self.refresh_access_token()

    def save_access_token(self, token_data):
        """Save access token and refresh token to .env file"""
        try:
            # Load existing .env content
            with open('.env', 'r') as f:
                content = f.read()
            
            # Update access token
            content = re.sub(r'STRAVA_ACCESS_TOKEN=[^\n]*', 
                          f'STRAVA_ACCESS_TOKEN={token_data["access_token"]}', 
                          content)
            
            # Update refresh token if present
            if "refresh_token" in token_data:
                content = re.sub(r'STRAVA_REFRESH_TOKEN=[^\n]*', 
                              f'STRAVA_REFRESH_TOKEN={token_data["refresh_token"]}', 
                              content, flags=re.IGNORECASE)
            
            # Update expires_at if present
            if "expires_at" in token_data:
                content = re.sub(r'STRAVA_EXPIRES_AT=[^\n]*', 
                              f'STRAVA_EXPIRES_AT={token_data["expires_at"]}', 
                              content, flags=re.IGNORECASE)
            
            # Write back to file
            with open('.env', 'w') as f:
                f.write(content)
            
            print("Access token and refresh token saved to .env file")
        except Exception as e:
            print(f"Error saving tokens: {str(e)}")
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

    def get_activities(self, days=7):
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
        
        print(f"\nFetching activities from last {days} days...")
        print(f"API URL: {url}")
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching activities: {response.text}")
            return []

    def analyze_fitness(self, activities):
        """Analyze fitness metrics from activities"""
        if not activities:
            print("No activities found")
            return

        # Calculate all-time fitness metrics
        total_distance_all = sum(activity['distance'] / 1000 for activity in activities)  # Convert from meters to km
        total_time_all = sum(activity['moving_time'] / 3600 for activity in activities)  # Convert from seconds to hours
        total_elevation_all = sum(activity['total_elevation_gain'] for activity in activities)
        avg_distance_all = total_distance_all / len(activities)
        avg_time_all = total_time_all / len(activities)
        avg_elevation_all = total_elevation_all / len(activities)

        # Filter activities from current week
        current_week_activities = []
        # Get current time in UTC (Strava timestamps are in UTC)
        today = datetime.now().astimezone()
        # Calculate start of week (Monday) in UTC
        start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)  # Monday
        
        print(f"\nAnalyzing activities:")
        
        for activity in activities:
            # Convert ISO 8601 timestamp to datetime
            activity_date = datetime.fromisoformat(activity['start_date_local'].replace('Z', '+00:00'))
            # Make the start_of_week timezone-aware with the same timezone
            if activity_date >= start_of_week:
                current_week_activities.append(activity)
                print(f"Found activity: {activity['name']} on {activity_date}")
            else:
                print(f"Skipping old activity: {activity['name']} on {activity_date}")

        if not current_week_activities:
            print("\nNo activities found for this week")
            return

        # Calculate weekly metrics
        total_distance = 0
        total_time = 0
        total_elevation = 0
        
        for activity in current_week_activities:
            total_distance += activity['distance'] / 1000  # Convert from meters to km
            total_time += activity['moving_time'] / 3600  # Convert from seconds to hours
            total_elevation += activity['total_elevation_gain']

        avg_distance = total_distance / len(current_week_activities)
        avg_time = total_time / len(current_week_activities)
        avg_elevation = total_elevation / len(current_week_activities)
        
        print("\n=== Weekly Fitness Summary ===")
        print(f"Total Distance: {total_distance:.2f} km")
        # Format time display (hours and minutes)
        total_hours = int(total_time)
        total_minutes = int((total_time - total_hours) * 60)
        time_display = f"{total_hours}h{total_minutes:02d}m" if total_hours > 0 else f"{total_time * 60:.0f} minutes"
        print(f"Total Time: {time_display}")
        
        # Calculate training load (distance in km per day)
        days_active = len(set(activity_date.date() for activity_date in 
                             [datetime.fromisoformat(a['start_date_local'].replace('Z', '+00:00')) 
                              for a in current_week_activities]))
        training_load = total_distance / days_active if days_active > 0 else 0
        
        # Determine fitness status based on all-time metrics
        fitness_status = ""
        if total_distance_all > 100:  # More than 100km total
            fitness_status = "Very Fit - High volume"
        elif total_distance_all > 50:  # 50-100km total
            fitness_status = "Fit - Good volume"
        elif total_distance_all > 20:  # 20-50km total
            fitness_status = "Moderate - Building fitness"
        else:  # Less than 20km total
            fitness_status = "Low - Need more activity"
        
        print(f"\nFitness Status: {fitness_status}")
        print(f"Training Load: {training_load:.2f} km/day")
        
        # Show weekly average metrics
        if current_week_activities:
            print("\n=== Weekly Average ===")
            print(f"Average Distance: {avg_distance:.2f} km")
            # Format average time display
            avg_hours = int(avg_time)
            avg_minutes = int((avg_time - avg_hours) * 60)
            avg_time_display = f"{avg_hours}h{avg_minutes:02d}m" if avg_hours > 0 else f"{avg_time * 60:.0f} minutes"
            print(f"Average Time: {avg_time_display}")
            print(f"Average Elevation Gain: {avg_elevation:.2f} m")
            print(f"Number of Activities: {len(current_week_activities)}")
        
        # Show all-time average metrics
        print("\n=== All-Time Average ===")
        print(f"Average Distance: {avg_distance_all:.2f} km")
        # Format all-time average time display
        avg_all_hours = int(avg_time_all)
        avg_all_minutes = int((avg_time_all - avg_all_hours) * 60)
        avg_all_time_display = f"{avg_all_hours}h{avg_all_minutes:02d}m" if avg_all_hours > 0 else f"{avg_time_all * 60:.0f} minutes"
        print(f"Average Time: {avg_all_time_display}")
        print(f"Average Elevation Gain: {avg_elevation_all:.2f} m")
        print(f"Total Activities: {len(activities)}")

if __name__ == "__main__":
    analyzer = StravaFitnessAnalyzer()
    
    # Try to get activities first - this will automatically refresh token if needed
    activities = analyzer.get_activities(days=7)
    
    if activities:
        analyzer.analyze_fitness(activities)
    else:
        # Only ask for authorization if we don't have a valid access token
        if not analyzer.access_token or analyzer.expires_at < time.time():
            print("\nAuthorization needed:")
            print("1. Visit this URL in your browser:")
            auth_url = f"https://www.strava.com/oauth/authorize?client_id={analyzer.client_id}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read,activity:read_all"
            print(f"{auth_url}")
            print("\n2. After authorizing, you'll be redirected to localhost with a URL like:")
            print("http://localhost/exchange_token?state=&code=YOUR_AUTH_CODE&scope=read,activity:read_all")
            print("\n3. Copy the code parameter (the long string after 'code=') and paste it here:")
            
            try:
                auth_code = input("Authorization code: ")
                token_data = analyzer.get_access_token(auth_code)
                if token_data:
                    print("\nSuccessfully obtained access token!")
                    print("The token has been saved to your .env file. You won't need to authorize again unless the token expires.")
                    print(f"Token will expire in {token_data.get('expires_in', 'unknown')} seconds")
                    
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
            print("\nNo activities found for this week. Make sure you have activities in your Strava account.")
