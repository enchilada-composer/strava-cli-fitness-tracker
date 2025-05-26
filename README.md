# Strava CLI Fitness Tracker

A command-line tool that provides a quick overview of your Strava fitness data, including:

```text
=== Weekly Fitness Summary ===
Total Distance: XX.XX km
Total Time: XX minutes

Fitness Status: [Your Status]
Training Load: XX.XX km/day

=== Weekly Average ===
Average Distance: XX.XX km
Average Time: XX minutes
Average Elevation Gain: XX.XX m
Number of Activities: X

=== All-Time Average ===
Average Distance: XX.XX km
Average Time: XX minutes
Average Elevation Gain: XX.XX m
Total Activities: X
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/enchilada-composer/strava-cli-fitness-tracker.git
cd strava-cli-fitness-tracker
mv .env.example .env
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

5. Update the `.env` file with your credentials:

```
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
```

6. Insert your CLIENT_ID in the URL and get an access token:
   - Visit: https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all

5. Run the script for the first time:
```bash
python strava_fitness.py
```

The script will guide you through the authorization process:
1. Visit the authorization URL shown in the terminal
2. Authorize the application
3. Copy the authorization code from the URL
4. Paste it back into the terminal

## Usage

Simply run the script:
```bash
python3 strava_fitness.py
```

The script will:
- Automatically refresh tokens when needed
- Fetch your activities from the last 7 days
- Show weekly and all-time statistics
- Track your training load
- Determine your fitness status

## Output Format

The script's output is organized into three main sections:

1. Weekly Fitness Summary:
```text
=== Weekly Fitness Summary ===
Total Distance: X.XX km
Total Time: XX minutes
Total Elevation Gain: X.XX m

Fitness Status: [status]
Training Load: X.XX km/day
```

2. Weekly Average:
```text
=== Weekly Average ===
Average Distance: X.XX km
Average Time: XX minutes
Average Elevation Gain: X.XX m
Number of Activities: X
```

3. All-Time Average:
```text
=== All-Time Average ===
Average Distance: X.XX km
Average Time: XX minutes
Average Elevation Gain: X.XX m
Total Activities: X
```

Time measurements are displayed in a readable format:
- For times less than 1 hour: `XX minutes`
- For times 1 hour or more: `XhXXm` (e.g., 1h30m for 1 hour 30 minutes)

Distances are shown in kilometers.

## Security

- Never commit your `.env` file to version control
- Keep your Strava credentials secure
- The script securely stores tokens in your `.env` file

## Troubleshooting

If you encounter any issues:
1. Check that your `.env` file has the correct credentials
2. Make sure you've authorized the application
3. Verify that your access token hasn't expired
4. Check the debug output for any error messages

## Requirements

- Python 3.8+
- Strava account
- Internet connection
- Valid Strava API credentials


## License

MIT License - feel free to use this tool for personal or commercial purposes
