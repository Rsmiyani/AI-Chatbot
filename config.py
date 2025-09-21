# config.py - NOAH AI Assistant Configuration
# ==========================================

# Gemini API Configuration
# Get your free API key from: https://aistudio.google.com
GEMINI_API_KEY = "XXXXXXXXXXXXXXXXXXXXXX"  # Replace with your actual API key

# Gemini Model Settings
GEMINI_MODEL = "gemini-1.5-flash"     # Model version to use
MAX_OUTPUT_TOKENS = 1000              # Maximum response length
TEMPERATURE = 0.7                     # Response creativity (0.0-2.0)
    
# Voice Assistant Settings
DEFAULT_USER_NAME = "Rudra"           # Default user name (from noah_data.json)
DEFAULT_CITY = "Mumbai"               # Default city for weather queries
VOICE_RATE = 120                      # Speech rate (words per minute)
VOICE_VOLUME = 1.0                    # Speech volume (0.0-1.0)

# Optional: Environment variables (alternative to hardcoding API key)
# You can set GEMINI_API_KEY as an environment variable instead
