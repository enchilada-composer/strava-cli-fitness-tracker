# Strava CLI Fitness Tracker

A command-line tool that provides a quick overview of your Strava fitness data, including:

```text
=== Weekly Fitness Summary ===
Total Distance: XX.XX km
Total Time: XX.XX hours
Total Elevation Gain: XX.XX m
Training Load: XX.XX

Fitness Status: [Your Status]

=== Average Per Activity ===
Average Distance: XX.XX km
Average Time: XX.XX hours
Average Elevation Gain: XX.XX m
```

The tool calculates your fitness status based on your training load and activity intensity:

1. **Training Load Calculation**
   - Training Load = Total Distance × Average Time
   - This metric combines volume (distance) and intensity (time) of your workouts

2. **Fitness Status Categories**
   - **High Training Load (> 100)**
     - Long Workouts (> 2 hours): "Fatigued - Consider reducing intensity"
     - Short Workouts: "Fit - Maintaining high training load"
   - **Moderate Training Load (50-100)**
     - Longer Workouts (> 1.5 hours): "Ready - Good balance of volume and intensity"
     - Shorter Workouts: "Fit - Building endurance"
   - **Low Training Load (< 50)**
     - Longer Workouts (> 1 hour): "Ready - Good recovery phase"
     - Shorter Workouts: "Fit - Maintaining base fitness"

These categories help you understand your current training state and provide guidance on whether you might need more recovery or if you're maintaining a good training balance.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/enchilada-composer/strava-cli-fitness-tracker.git
cd strava-cli-fitness-tracker
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure Strava API:
   - Go to https://www.strava.com/settings/api
   - Click "Create Application" (if you have an existing application, you'll need to edit it)
   - Fill in the details:
     - Name: Strava CLI Fitness Tracker
     - Website: https://github.com/enchilada-composer/strava-cli-fitness-tracker
     - Description: Personal fitness tracking tool
     - Authorization callback domain: localhost
   - Click "Register" or "Save"
   - Note down your Client ID and Client Secret

5. Create a `.env` file with your credentials:
```
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
```

6. Insert your CLIENT_ID in the URL and get an access token:
   - Visit: https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all
   - Authorize the application
   - Copy the authorization code from the URL
   - The script will automatically fetch an access token

## Features

- Weekly activity summary (distance, speed, time)
- Fitness analysis and fatigue status
- Elevation gain tracking
- Activity statistics (per session and average)
- No visualizations (text-based output only)

## Usage

Run the script:
```bash
python strava_fitness.py
```

The script will output:
- Current week's activity summary
- Fitness analysis based on training load
- Weekly progress metrics

## Requirements

- Python 3.8+
- Strava API access
- Virtual environment (recommended)


## License

MIT License - feel free to use this tool for personal or commercial