import subprocess
import platform
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('OpenApps')

# Dictionary mapping common app names to their executable paths or commands
# These will need to be customized based on the user's system
WINDOWS_APPS = {
    "calculator": "calc.exe",
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge": "msedge.exe",
    "whatsapp": r"C:\Users\%USERNAME%\AppData\Local\WhatsApp\WhatsApp.exe",
    "youtube": "https://www.youtube.com/",
    "spotify": r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
    "mail": "outlook.exe",
    "file explorer": "explorer.exe",
    "settings": "ms-settings:",
    "camera": "microsoft.windows.camera:",
    "calendar": "outlookcal:",
    "photos": "ms-photos:",
}

MAC_APPS = {
    "calculator": "open -a Calculator",
    "notes": "open -a Notes",
    "safari": "open -a Safari",
    "chrome": "open -a 'Google Chrome'",
    "firefox": "open -a Firefox",
    "whatsapp": "open -a WhatsApp",
    "youtube": "open https://www.youtube.com/",
    "spotify": "open -a Spotify",
    "mail": "open -a Mail",
    "finder": "open -a Finder",
    "system preferences": "open -a 'System Preferences'",
    "camera": "open -a 'Photo Booth'",
    "calendar": "open -a Calendar",
    "photos": "open -a Photos",
}

LINUX_APPS = {
    "calculator": "gnome-calculator",
    "text editor": "gedit",
    "firefox": "firefox",
    "chrome": "google-chrome",
    "chromium": "chromium-browser",
    "nautilus": "nautilus",
    "files": "nautilus",
    "file explorer": "nautilus",
    "settings": "gnome-control-center",
    "terminal": "gnome-terminal",
    "youtube": "firefox https://www.youtube.com/",
}

def get_app_command(app_name):
    """
    Get the command to open an application based on the operating system.
    
    Args:
        app_name (str): The name of the application to open
        
    Returns:
        str or None: The command to open the application, or None if not found
    """
    app_name = app_name.lower()
    
    system = platform.system()
    
    if system == "Windows":
        # Handle web URLs differently
        if app_name == "youtube":
            return f"start {WINDOWS_APPS['youtube']}"
        elif app_name in WINDOWS_APPS:
            return f"start {WINDOWS_APPS[app_name]}"
        # Try to open by name if not in predefined list
        return f"start {app_name}"
        
    elif system == "Darwin":  # macOS
        if app_name in MAC_APPS:
            return MAC_APPS[app_name]
        # Try to open by name if not in predefined list
        return f"open -a '{app_name}'"
        
    elif system == "Linux":
        if app_name in LINUX_APPS:
            return LINUX_APPS[app_name]
        # Try to open by name if not in predefined list
        return app_name
    
    return None

def open_app(app_name):
    """
    Open an application using the appropriate command for the current operating system.
    
    Args:
        app_name (str): The name of the application to open
        
    Returns:
        bool: True if the application was opened successfully, False otherwise
    """
    try:
        logger.info(f"Attempting to open: {app_name}")
        
        # Extract app name from the command
        app_name = app_name.lower().strip()
        
        # Get the command to open the application
        command = get_app_command(app_name)
        
        if not command:
            logger.error(f"No command found for app: {app_name}")
            return False
        
        logger.info(f"Executing command: {command}")
        
        # Execute the command
        if platform.system() == "Windows":
            subprocess.Popen(command, shell=True)
        else:
            os.system(command)
            
        logger.info(f"Successfully opened: {app_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error opening {app_name}: {str(e)}")
        return False

# If run directly, test the module
if __name__ == "__main__":
    test_apps = ["calculator", "notepad", "chrome", "youtube"]
    
    for app in test_apps:
        print(f"Testing opening: {app}")
        result = open_app(app)
        print(f"Result: {'Success' if result else 'Failed'}")