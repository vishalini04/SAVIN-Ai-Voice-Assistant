from flask import Flask, render_template, request, jsonify, send_file
import os
import logging
from flask_cors import CORS
from PIL import Image, ImageDraw
import io
import json
import datetime

# Import our custom modules
from VoiceAssistant_main import process_voice_command, simple_response
from openapps import open_app
from reminder import set_reminder_with_details
from textRead import write_in_notepad

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='savin_app.log'
)
logger = logging.getLogger('SavinApp')

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return "Error loading the application. Check logs for details.", 500
@app.route('/api/process_command', methods=['POST'])
def api_process_command():
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'response': "I couldn't hear you. Please try again."})
        logger.info(f"Received query: {query}")
        
        # Extract command type
        query_lower = query.lower()
        
        # Handle opening applications
        if "open" in query_lower:
            app_name = query_lower.replace("open", "").strip()
            if app_name:
                result = open_app(app_name)
                if result:
                    return jsonify({'response': f"Opening {app_name}"})
                else:
                    return jsonify({'response': f"I couldn't find or open {app_name}. Can you try with a different application?"})
            else:
                return jsonify({'response': "Which app would you like me to open?"})
        # Handle reminders
        elif "remind me" in query_lower or "set a reminder" in query_lower or "reminder" in query_lower:
            # Try to extract time and message from the query
            time_parts = ["at", "in", "on", "for", "tomorrow", "today"]
            time_str = None
            message = None
            
            for part in time_parts:
                if part in query_lower:
                    split_query = query_lower.split(part, 1)
                    if len(split_query) > 1:
                        time_str = part + split_query[1]
                        message = split_query[0].replace("remind me", "").replace("set a reminder", "").replace("reminder", "").strip()
                        break
            
            if time_str and message:
                result = set_reminder_with_details(time_str, message)
                return jsonify(result)
            else:
                return jsonify({
                    'response': "I'd like to set a reminder for you. Please tell me when and what to remind you about. For example, 'Remind me to call mom at 5pm'."
                })
        # Handle note taking
        elif "write" in query_lower or "note" in query_lower or "take a note" in query_lower:
            note_text = query_lower
            for prefix in ["write", "note", "take a note", "write a note", "type"]:
                note_text = note_text.replace(prefix, "").strip()
            
            if note_text:
                success = write_in_notepad(note_text)
                if success:
                    return jsonify({'response': f"I've written your note: {note_text}"})
                else:
                    return jsonify({'response': "I had trouble writing that note. Could you try again?"})
            else:
                return jsonify({'response': "What would you like me to write down?"})
                
        # Process general voice commands
        else:
            response = process_voice_command(query)
            return jsonify({'response': response})
            
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        return jsonify({'response': "I encountered an error processing your request. Please try again."})

@app.route('/api/simple_response', methods=['POST'])
def api_simple_response():
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'response': "I couldn't understand that. Please try again."})
            
        response = simple_response(query)
        return jsonify({'response': response})
        
    except Exception as e:
        logger.error(f"Error generating simple response: {e}")
        return jsonify({'response': "I had trouble processing that. Could you try again?"})

@app.route('/api/status', methods=['GET'])
def api_status():
    """
    Check if the Ollama API is running
    """
    try:
        # Import the Ollama module
        try:
            from chat import chat_with_ollama
            # Try a simple query to check if Ollama is working
            response = chat_with_ollama("test", model="mistral")
            ollama_status = "running"
        except ImportError:
            ollama_status = "not_installed"
        except Exception:
            ollama_status = "error"
            
        return jsonify({
            'status': 'running',
            'ollama_status': ollama_status,
            'time': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/log_activity', methods=['POST'])
def log_activity():
    try:
        data = request.json
        activity_type = data.get('type', 'unspecified')
        details = data.get('details', {})
        
        # Create log entry
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': activity_type,
            'details': details
        }
        
        # Append to activity log file
        with open('activity_log.json', 'a+') as f:
            # Check if file is empty
            f.seek(0)
            content = f.read().strip()
            if not content:
                json.dump([log_entry], f)
            else:
                f.seek(0)
                try:
                    existing_logs = json.load(f)
                    existing_logs.append(log_entry)
                    f.seek(0)
                    f.truncate()
                    json.dump(existing_logs, f)
                except json.JSONDecodeError:
                    # If file is corrupted, start fresh
                    f.seek(0)
                    f.truncate()
                    json.dump([log_entry], f)
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error logging activity: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/get_activity_log', methods=['GET'])
def get_activity_log():
    try:
        if os.path.exists('activity_log.json'):
            with open('activity_log.json', 'r') as f:
                logs = json.load(f)
                return jsonify(logs)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Error retrieving activity log: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = 5000
    logger.info(f"Starting Savin Assistant application on http://localhost:{port}")
    print(f"Starting Savin Assistant application on http://localhost:{port}")
    app.run(debug=True, port=port)