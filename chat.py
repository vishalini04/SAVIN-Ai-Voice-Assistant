import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('OllamaChat')

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def chat_with_ollama(query, model="mistral", system_prompt=None):
    """
    Send a query to Ollama API and get a response.
    
    Args:
        query (str): The user's query
        model (str): The model to use (default: "mistral")
        system_prompt (str): Optional system prompt to guide the model's behavior
        
    Returns:
        str: The model's response or an error message
    """
    try:
        # Prepare request payload
        payload = {
            "model": model,
            "prompt": query,
            "stream": False
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt
        
        logger.info(f"Sending query to Ollama: {query[:50]}...")
        
        # Send request to Ollama API
        response = requests.post(OLLAMA_API_URL, json=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("response", "I couldn't generate a response.")
        else:
            logger.error(f"Error from Ollama API: {response.status_code} - {response.text}")
            return "I'm having trouble connecting to my language model. Please try again later."
    
    except requests.exceptions.ConnectionError:
        logger.error("Connection error: Unable to connect to Ollama API")
        return "I can't reach my language model right now. Please make sure Ollama is running locally on port 11434."
    
    except Exception as e:
        logger.error(f"Error chatting with Ollama: {str(e)}")
        return "I encountered an error while processing your request. Please try again."

# Define a system prompt for the assistant's personality
DEFAULT_SYSTEM_PROMPT = """
You are Savin, a helpful voice assistant. You should be concise, friendly, and helpful.
Respond to user queries in a natural, conversational way. Keep responses brief but informative.
If asked about your capabilities, mention you can open apps, set reminders, take notes, and have conversations.
"""

def get_chat_response(query):
    """
    Get a chat response from Ollama with the default system prompt.
    
    Args:
        query (str): The user's query
        
    Returns:
        str: The model's response
    """
    return chat_with_ollama(query, system_prompt=DEFAULT_SYSTEM_PROMPT)

# Test the module if run directly
if __name__ == "__main__":
    test_queries = [
        "Hello, how are you today?",
        "What's the capital of France?",
        "Tell me a short joke",
        "What can you do?"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        print(f"Response: {get_chat_response(query)}")
        print()