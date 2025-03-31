import datetime
import json
import os
import threading
import time
import platform
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Reminder')

# File to store reminders
REMINDERS_FILE = "reminders.json"

def get_reminders_file_path():
    """Get the full path to the reminders file."""
    # Store in user's home directory
    home_dir = Path.home()
    savin_dir = home_dir / ".savin"
    
    # Create directory if it doesn't exist
    if not savin_dir.exists():
        savin_dir.mkdir(exist_ok=True)
    
    return savin_dir / REMINDERS_FILE

def load_reminders():
    """Load existing reminders from file."""
    reminders_file = get_reminders_file_path()
    
    if reminders_file.exists():
        try:
            with open(reminders_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Could not decode reminders file. Starting with empty reminders.")
            return []
    else:
        return []

def save_reminders(reminders):
    """Save reminders to file."""
    reminders_file = get_reminders_file_path()
    
    try:
        with open(reminders_file, 'w') as f:
            json.dump(reminders, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving reminders: {str(e)}")
        return False

def parse_time(time_str):
    """
    Parse a time string into a datetime object.
    
    Args:
        time_str (str): A string representing a time, like "tomorrow at 3pm" or "in 5 minutes"
        
    Returns:
        datetime.datetime: A datetime object representing the parsed time, or None if parsing failed
    """
    time_str = time_str.lower()
    now = datetime.datetime.now()
    
    try:
        # Handle "in X minutes/hours"
        if "in " in time_str:
            parts = time_str.split("in ")[1].split()
            if len(parts) >= 2:
                amount = int(parts[0])
                unit = parts[1]
                
                if "minute" in unit:
                    return now + datetime.timedelta(minutes=amount)
                elif "hour" in unit:
                    return now + datetime.timedelta(hours=amount)
        
        # Handle "tomorrow at X" or "today at X"
        elif "tomorrow at " in time_str:
            time_part = time_str.split("tomorrow at ")[1]
            tomorrow = now + datetime.timedelta(days=1)
            return parse_time_of_day(time_part, tomorrow)
        elif "today at " in time_str:
            time_part = time_str.split("today at ")[1]
            return parse_time_of_day(time_part, now)
        
        # Handle direct time specification like "3pm" or "15:00"
        else:
            return parse_time_of_day(time_str, now)
            
    except Exception as e:
        logger.error(f"Error parsing time '{time_str}': {str(e)}")
        return None

def parse_time_of_day(time_str, base_date):
    """
    Parse a time of day string and combine it with a base date.
    
    Args:
        time_str (str): A string representing a time of day, like "3pm" or "15:00"
        base_date (datetime.datetime): The base date to combine with the time
        
    Returns:
        datetime.datetime: A datetime object combining the base date and parsed time
    """
    # Handle "Xpm" or "Xam"
    if "pm" in time_str:
        hour = int(time_str.replace("pm", "").strip())
        hour = hour if hour == 12 else hour + 12
        return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    elif "am" in time_str:
        hour = int(time_str.replace("am", "").strip())
        hour = 0 if hour == 12 else hour
        return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    
    # Handle "HH:MM" format
    elif ":" in time_str:
        hour, minute = map(int, time_str.split(":"))
        return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Default to noon if format isn't recognized
    else:
        return base_date.replace(hour=12, minute=0, second=0, microsecond=0)

def add_reminder(time_str, message):
    """
    Add a new reminder.
    
    Args:
        time_str (str): When to remind, like "tomorrow at 3pm" or "in 5 minutes"
        message (str): What to remind the user about
        
    Returns:
        bool: True if the reminder was added successfully, False otherwise
    """
    try:
        reminder_time = parse_time(time_str)
        
        if not reminder_time:
            logger.error(f"Could not parse time: {time_str}")
            return False
        
        # If reminder time is in the past, set it to tomorrow
        if reminder_time < datetime.datetime.now():
            reminder_time = reminder_time + datetime.timedelta(days=1)
        
        # Load existing reminders
        reminders = load_reminders()
        
        # Add new reminder
        reminder = {
            "time": reminder_time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message
        }
        
        reminders.append(reminder)
        
        # Save updated reminders
        return save_reminders(reminders)
        
    except Exception as e:
        logger.error(f"Error adding reminder: {str(e)}")
        return False

def check_reminders():
    """Check for due reminders and notify the user."""
    try:
        reminders = load_reminders()
        now = datetime.datetime.now()
        updated = False
        
        # Check each reminder
        remaining_reminders = []
        for reminder in reminders:
            reminder_time = datetime.datetime.strptime(reminder["time"], "%Y-%m-%d %H:%M:%S")
            
            # If reminder is due, notify the user
            if reminder_time <= now:
                notify_user(reminder["message"])
                updated = True
            else:
                remaining_reminders.append(reminder)
        
        # Save updated reminders if any were removed
        if updated:
            save_reminders(remaining_reminders)
            
    except Exception as e:
        logger.error(f"Error checking reminders: {str(e)}")

def notify_user(message):
    """
    Show a notification to the user.
    
    Args:
        message (str): The message to show in the notification
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            # For Windows, use the built-in notification system
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast("Savin Reminder", message, duration=10)
        elif system == "Darwin":  # macOS
            # For macOS, use the osascript command
            os.system(f'osascript -e \'display notification "{message}" with title "Savin Reminder"\'')
        elif system == "Linux":
            # For Linux, use the notify-send command
            os.system(f'notify-send "Savin Reminder" "{message}"')
            
        logger.info(f"Notification displayed: {message}")
        
    except Exception as e:
        logger.error(f"Error displaying notification: {str(e)}")

def reminder_checker_thread():
    """Background thread to periodically check for due reminders."""
    while True:
        check_reminders()
        time.sleep(60)  # Check every minute

def start_reminder_checker():
    """Start the background thread to check for reminders."""
    thread = threading.Thread(target=reminder_checker_thread, daemon=True)
    thread.start()
    logger.info("Reminder checker thread started")

def set_reminder_voice():
    """
    Function to handle voice-initiated reminders.
    When called from the app.py, this will just return the response.
    The actual reminder setting will be handled through the API endpoint
    with the specific time and message.
    """
    return {
        "response": "I'd be happy to set a reminder for you. Please let me know what you'd like to be reminded about and when."
    }

def set_reminder_with_details(time_str, message):
    """
    Set a reminder with the given time and message.
    
    Args:
        time_str (str): When to remind, like "tomorrow at 3pm" or "in 5 minutes"
        message (str): What to remind the user about
        
    Returns:
        dict: Response indicating success or failure
    """
    success = add_reminder(time_str, message)
    
    if success:
        # Get the reminder time for the response
        reminder_time = parse_time(time_str)
        time_str = reminder_time.strftime("%A, %B %d at %I:%M %p") if reminder_time else time_str
        
        return {
            "response": f"I've set a reminder for {time_str} about: {message}"
        }
    else:
        return {
            "response": "I'm sorry, I couldn't set that reminder. Please try again with a different time format."
        }

# Start the reminder checker when the module is imported
start_reminder_checker()

# If run directly, test the module
if __name__ == "__main__":
    print("Testing reminder system...")
    
    # Test adding a reminder
    print("Adding test reminder in 1 minute...")
    result = add_reminder("in 1 minutes", "Test reminder")
    print(f"Result: {'Success' if result else 'Failed'}")
    
    # Keep the script running to see the notification
    print("Waiting for reminder to trigger (check every 10 seconds)...")
    for _ in range(6):  # Check for 1 minute
        check_reminders()
        time.sleep(10)