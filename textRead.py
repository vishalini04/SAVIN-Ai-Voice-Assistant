import os
import platform
import subprocess
import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('NotesTaker')

def get_notes_directory():
    """Get the directory where notes will be stored."""
    home_dir = Path.home()
    notes_dir = home_dir / "Savin Notes"
    
    # Create the directory if it doesn't exist
    if not notes_dir.exists():
        notes_dir.mkdir(exist_ok=True)
        logger.info(f"Created notes directory: {notes_dir}")
    
    return notes_dir

def write_in_notepad(text):
    """
    Write the given text to a notepad file.
    
    Args:
        text (str): The text to write to the file
        
    Returns:
        bool: True if the note was written successfully, False otherwise
    """
    try:
        # Create a timestamped file name
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        notes_dir = get_notes_directory()
        file_path = notes_dir / f"note_{timestamp}.txt"
        
        # Write the text to the file
        with open(file_path, 'w') as f:
            f.write(text)
        
        logger.info(f"Note written to: {file_path}")
        
        # Attempt to open the file with the default text editor
        open_file_with_default_app(file_path)
        
        return True
        
    except Exception as e:
        logger.error(f"Error writing note: {str(e)}")
        return False

def open_file_with_default_app(file_path):
    """
    Open a file with the default application.
    
    Args:
        file_path (str or Path): Path to the file to open
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.call(["open", str(file_path)])
        else:  # Linux
            subprocess.call(["xdg-open", str(file_path)])
        
        logger.info(f"Opened file: {file_path}")
        
    except Exception as e:
        logger.error(f"Error opening file: {str(e)}")

def list_recent_notes(limit=5):
    """
    List the most recent notes.
    
    Args:
        limit (int): Maximum number of notes to list
        
    Returns:
        list: List of recent note files
    """
    try:
        notes_dir = get_notes_directory()
        note_files = sorted(list(notes_dir.glob("note_*.txt")), key=os.path.getmtime, reverse=True)
        
        return note_files[:limit]
        
    except Exception as e:
        logger.error(f"Error listing notes: {str(e)}")
        return []

def get_note_content(file_path):
    """
    Get the content of a note file.
    
    Args:
        file_path (str or Path): Path to the note file
        
    Returns:
        str: The content of the note
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading note: {str(e)}")
        return ""

# If run directly, test the module
if __name__ == "__main__":
    print("Testing note taking system...")
    
    # Test writing a note
    test_note = "This is a test note created at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Writing test note: {test_note}")
    
    result = write_in_notepad(test_note)
    print(f"Result: {'Success' if result else 'Failed'}")
    
    # Test listing recent notes
    print("\nRecent notes:")
    recent_notes = list_recent_notes()
    for i, note_file in enumerate(recent_notes, 1):
        print(f"{i}. {note_file.name}")
        content = get_note_content(note_file)
        print(f"   Content: {content[:50]}...")