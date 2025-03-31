import random
import datetime
import json
import os
import platform
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='savin.log'
)
logger = logging.getLogger('Savin')

try:
    from chat import get_chat_response
    OLLAMA_AVAILABLE = True
    logger.info("Ollama chat module loaded successfully")
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama chat module not available. Falling back to simple responses.")

# Generic responses for different types of queries
GREETINGS = [
    "Hello! How can I help you today?",
    "Hi there! I'm Savin, ready to assist you.",
    "Greetings! What can I do for you?",
    "Hello! I'm here to help. What do you need?"
]

FAREWELLS = [
    "Goodbye! Have a great day!",
    "See you later! Take care!",
    "Bye for now! Let me know if you need anything else.",
    "Farewell! I'll be here when you need me."
]

ACKNOWLEDGEMENTS = [
    "I understand. Let me help with that.",
    "Got it. I'll assist you right away.",
    "I see what you need. Working on it now.",
    "Understood. I'm on it."
]

CONFUSIONS = [
    "I'm not sure I understand. Could you phrase that differently?",
    "I didn't quite catch that. Can you please clarify?",
    "I'm having trouble understanding. Could you be more specific?",
    "I'm not following. Can you explain in a different way?"
]

def process_voice_command(query):
    """
    Process natural language commands from the user and determine the appropriate action.
    
    Args:
        query (str): The user's voice command or text input
        
    Returns:
        str: The response to the user's command
    """
    logger.info(f"Processing command: {query}")
    
    # Convert to lowercase for easier matching
    query = query.lower().strip()
    
    # Handle greetings
    if any(word in query for word in ["hello", "hi", "hey", "greetings"]):
        return random.choice(GREETINGS)
    
    # Handle farewells
    elif any(word in query for word in ["bye", "goodbye", "see you", "farewell"]):
        return random.choice(FAREWELLS)
    
    # Handle time queries
    elif "time" in query:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."
    
    # Handle date queries
    elif "date" in query or "day" in query:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}."
    
    # Handle weather queries (placeholder - would need API integration)
    elif "weather" in query:
        return "I don't have access to real-time weather data right now, but I can help you with other things."
    
    # Handle basic questions about the assistant
    elif "who are you" in query or "your name" in query:
        return "I'm Savin, your personal AI assistant. I can help you with opening apps, setting reminders, taking notes, and having conversations."
    
    # Handle capability questions
    elif "what can you do" in query or "help me" in query or "your capabilities" in query:
        return "I can open applications for you, set reminders, take notes, tell you the time and date, and have a friendly conversation. Just tell me what you need!"
    
    # Determine if this is a command we should handle directly
    if "open" in query:
        # This will be handled by the dedicated function in openapps.py
        # Just return a conversational acknowledgment
        return "I'll open that for you right away."
    
    elif any(phrase in query for phrase in ["set a reminder", "remind me", "create a reminder"]):
        # This will be handled by the dedicated function in reminder.py
        return "I'd be happy to set a reminder for you. What would you like me to remind you about?"
    
    elif any(phrase in query for phrase in ["take a note", "write this down", "make a note", "write a note"]):
        # This will be handled by the dedicated function in textRead.py
        return "I'll take a note for you. What would you like me to write down?"
    
    else:
        # For general chit-chat or unknown commands, provide a friendly response
        return simple_response(query)

def simple_response(query):
    """
    Provide a simple rule-based response for general conversation.
    
    Args:
        query (str): The user's input
        
    Returns:
        str: A response to the user
    """
    if OLLAMA_AVAILABLE:
        try:
            return get_chat_response(query)
        except Exception as e:
            logger.error(f"Error getting Ollama response: {e}")
            # Fall back to rule-based responses
    query = query.lower()
    
    # Check if user is asking how the assistant is
    if any(phrase in query for phrase in ["how are you", "how's it going", "how do you do"]):
        return "I'm doing well, thank you for asking! How can I help you today?"
    
    # Check if user is expressing gratitude
    elif any(word in query for word in ["thanks", "thank you", "appreciate"]):
        return "You're welcome! I'm happy to help."
    
    # Check if user is asking about capabilities
    elif any(phrase in query for phrase in ["can you", "are you able to"]):
        return "I can help you open applications, set reminders, take notes, and more. Just let me know what you need!"
    
    # Default response for unknown queries
    else:
        return random.choice([
            "I'm not sure how to help with that specific request, but I can open apps, set reminders, or take notes for you.",
            "I didn't quite understand. Could you try rephrasing or ask me to open an app, set a reminder, or take a note?",
            "I'm still learning! I can definitely help you open applications, set reminders, or write notes though.",
            "Let me know if you'd like me to open an application, set a reminder, or take a note for you."
        ])

# If run directly, test the module
if __name__ == "__main__":
    test_queries = [
        "Hello there",
        "What time is it?",
        "Open calculator",
        "Set a reminder for my meeting",
        "Take a note: buy milk tomorrow",
        "What's the weather like?",
        "Who are you?",
        "Thank you for your help",
        "Goodbye for now"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        print(f"Response: {process_voice_command(query)}")
        print()