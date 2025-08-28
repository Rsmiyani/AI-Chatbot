import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import datetime
import subprocess
import psutil
import wikipedia
import pyjokes
import time
import random
import json
import requests
import pyautogui
import cv2
import platform
import tempfile
import re
import threading
import warnings
import urllib.parse
import logging
import sys
from pathlib import Path

warnings.filterwarnings('ignore')

# Import config settings
try:
    from config import DEFAULT_USER_NAME, DEFAULT_CITY, VOICE_RATE, VOICE_VOLUME
except ImportError:
    print("⚠️ Config file not found. Using default settings.")
    DEFAULT_USER_NAME = "Master"
    DEFAULT_CITY = "Mumbai"
    VOICE_RATE = 120
    VOICE_VOLUME = 1.0

# Import the Gemini-only chatbot functionality
from chatbot_core import EnhancedChatbot

class NOAHLogger:
    """Enhanced logging system for NOAH AI Assistant"""
    def __init__(self, log_file="noah_assistant.log"):
        # Create logger
        self.logger = logging.getLogger('NOAH_AI')
        self.logger.setLevel(logging.DEBUG)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            # Create formatters
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_formatter = logging.Formatter(
                '🤖 %(levelname)s: %(message)s'
            )
            
            # File handler
            try:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"⚠️ Could not create log file: {e}")
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def debug(self, message):
        self.logger.debug(message)

class AdvancedNOAHWithAI:
    def __init__(self):
        print("🤖 Initializing NOAH AI Assistant...")
        print("📁 Loading configuration from config.py...")
        
        # Initialize logging
        self.logger = NOAHLogger()
        self.logger.info("NOAH AI Assistant initialization started")
        
        # Initialize text-to-speech with config settings
        try:
            self.engine = pyttsx3.init()
            self.setup_voice()
            self.logger.info("Text-to-speech engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Text-to-speech initialization failed: {e}")
            self.engine = None

        # Initialize speech recognition with fallback
        self.text_mode = False
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.logger.info("Speech recognition initialized successfully")
        except Exception as e:
            self.logger.warning(f"Speech recognition initialization failed: {e}")
            self.logger.info("Switching to text input mode")
            self.microphone = None
            self.text_mode = True

        self.is_listening = True
        self.user_name = DEFAULT_USER_NAME
        self.user_data = self.load_user_data()
        
        # Initialize the Gemini-only chatbot
        self.chatbot = EnhancedChatbot()
        self.ai_model_loaded = False
        
        # Show API status
        print(f"🔑 API Status: {self.chatbot.get_api_status()}")
        
        # Adjust for ambient noise (only if microphone available)
        if self.microphone and not self.text_mode:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.logger.info("Microphone calibrated for ambient noise")
            except Exception as e:
                self.logger.warning(f"Microphone calibration failed: {e}")
                self.text_mode = True

    def setup_voice(self):
        """Configure voice properties from config"""
        try:
            if self.engine:
                self.engine.setProperty('rate', VOICE_RATE)
                self.engine.setProperty('volume', VOICE_VOLUME)
                voices = self.engine.getProperty('voices')
                if len(voices) > 1:
                    self.engine.setProperty('voice', voices[1].id)
                self.logger.debug("Text-to-speech engine configured from config")
        except Exception as e:
            self.logger.error(f"Voice setup failed: {e}")

    def say(self, text):
        """Text-to-speech function with error handling"""
        print(f"NOAH: {text}")
        self.logger.info(f"Response: {text}")
        try:
            if self.engine:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Speech output failed: {e}")

    def get_input(self):
        """Get input via voice or text fallback"""
        if self.text_mode:
            print("\n🎯 Text Mode Active (Voice unavailable or disabled)")
            try:
                query = input("💬 Type your command: ").strip().lower()
                if query:
                    print(f"👤 User typed: {query}")
                    self.logger.info(f"User input (text): {query}")
                return query
            except (KeyboardInterrupt, EOFError):
                return "exit"
            except Exception as e:
                self.logger.error(f"Text input error: {e}")
                return ""
        else:
            return self.listen()

    def listen(self):
        """Listen for voice commands with better error handling"""
        if not self.microphone or self.text_mode:
            return self.get_input()
        
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                self.recognizer.pause_threshold = 1
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            print("🧠 Recognizing...")
            query = self.recognizer.recognize_google(audio, language="en-in")
            print(f"👤 User said: {query}")
            self.logger.info(f"User input (voice): {query}")
            return query.lower()
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            self.say("Sorry, my speech service is having issues. Switching to text mode.")
            self.logger.error(f"Speech recognition service error: {e}")
            self.text_mode = True
            return ""
        except Exception as e:
            self.logger.error(f"Unexpected listening error: {e}")
            return ""

    def load_user_data(self):
        """Load user preferences from file"""
        try:
            if os.path.exists('noah_data.json'):
                with open('noah_data.json', 'r') as f:
                    data = json.load(f)
                self.user_name = data.get("name", DEFAULT_USER_NAME)
                self.logger.info(f"User data loaded for {self.user_name}")
                return data
        except Exception as e:
            self.logger.error(f"Failed to load user data: {e}")
        return {"name": DEFAULT_USER_NAME, "preferences": {}, "conversation_history": []}

    def save_user_data(self):
        """Save user preferences to file"""
        try:
            with open('noah_data.json', 'w') as f:
                json.dump(self.user_data, f, indent=2)
            self.logger.debug("User data saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save user data: {e}")

    def initialize_ai_model(self):
        """Initialize Gemini AI model - Uses config file"""
        try:
            self.say("Loading advanced Gemini AI model from configuration...")
            self.logger.info("Loading Gemini model from config...")
            
            # Load using config file settings
            success = self.chatbot.load_gemini_api()
            
            if success:
                self.ai_model_loaded = True
                self.say("Gemini AI model loaded successfully from config! I'm now powered by Google's advanced AI.")
                self.logger.info("Gemini model loaded successfully from config")
                return True
            else:
                self.say("Failed to load Gemini AI model. Please check your API key in config.py file.")
                self.logger.error("Failed to load Gemini model")
                print("\n📝 To fix this:")
                print("1. Open config.py file")
                print("2. Replace 'YOUR_API_KEY_HERE' with your actual API key")
                print("3. Save the file and try again")
                return False
                
        except Exception as e:
            self.say("Error loading Gemini AI model from configuration")
            self.logger.error(f"Model loading error: {e}")
            return False

    def smart_search(self, query, platform="google"):
        """Enhanced smart search with better URL handling"""
        try:
            # URL encode the query to handle spaces and special characters
            encoded_query = urllib.parse.quote_plus(query)
            search_urls = {
                "google": f"https://www.google.com/search?q={encoded_query}",
                "youtube": f"https://www.youtube.com/results?search_query={encoded_query}",
                "amazon": f"https://www.amazon.com/s?k={encoded_query}",
                "github": f"https://github.com/search?q={encoded_query}",
                "wikipedia": f"https://en.wikipedia.org/wiki/Special:Search?search={encoded_query}"
            }
            
            url = search_urls.get(platform, search_urls["google"])
            self.logger.info(f"Opening {platform} search for: {query}")
            
            # Try multiple methods to open browser
            success = False
            try:
                # Method 1: Use webbrowser module
                webbrowser.open(url)
                success = True
                self.logger.debug(f"Opened {platform} using webbrowser module")
            except Exception as e1:
                self.logger.warning(f"webbrowser.open failed: {e1}")
                try:
                    # Method 2: Use system-specific commands
                    if platform.system() == "Windows":
                        os.system(f'start "" "{url}"')
                        success = True
                        self.logger.debug(f"Opened {platform} using Windows start command")
                    elif platform.system() == "Darwin":  # macOS
                        os.system(f'open "{url}"')
                        success = True
                        self.logger.debug(f"Opened {platform} using macOS open command")
                    else:  # Linux
                        os.system(f'xdg-open "{url}"')
                        success = True
                        self.logger.debug(f"Opened {platform} using Linux xdg-open command")
                except Exception as e2:
                    self.logger.warning(f"OS command failed: {e2}")
            
            if success:
                return f"Opening {platform} and searching for {query}"
            else:
                return f"Could not open {platform}. Please check your default browser settings."
                
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return f"Error occurred while trying to search {platform}"

    def handle_tell_me_about(self, query):
        """Handle 'tell me about' requests using Gemini AI"""
        try:
            # Extract topic
            patterns = [
                r'tell me about (.+)',
                r'what is (.+)',
                r'explain (.+)',
                r'describe (.+)',
                r'information about (.+)',
                r'write about (.+)'
            ]
            
            topic = None
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    topic = match.group(1).strip()
                    break
            
            if not topic:
                return "I didn't catch what you want to know about. Please say 'tell me about' followed by a topic."
            
            self.logger.info(f"Generating information about: {topic}")
            
            # Load AI model if not loaded
            if not self.ai_model_loaded:
                self.say("Let me load my advanced AI knowledge base first...")
                if not self.initialize_ai_model():
                    self.say("Using Wikipedia for information...")
                    try:
                        wiki_info = wikipedia.summary(topic, sentences=5)
                        filename = self.save_and_open_notepad(topic, f"Wikipedia Information:\n\n{wiki_info}")
                        return f"I couldn't load the AI model, but I found Wikipedia information about {topic}."
                    except Exception as e:
                        self.logger.error(f"Wikipedia fallback error: {e}")
                        return "Sorry, I couldn't load the AI model or find Wikipedia information."
            
            self.say(f"Let me use advanced AI to generate detailed information about {topic}...")
            
            # Generate comprehensive information using Gemini
            prompts = [
                f"Provide a comprehensive overview of {topic}, including key facts, importance, and applications.",
                f"What are the main features and characteristics of {topic}? Include examples and practical uses.",
            ]
            
            ai_responses = []
            for i, prompt in enumerate(prompts):
                try:
                    self.logger.debug(f"AI generating section {i+1}/2...")
                    response = self.chatbot.get_response(prompt)
                    if response and len(response.strip()) > 50:
                        ai_responses.append(f"AI Analysis {i+1}:\n{response.strip()}")
                        self.logger.debug(f"AI generated section {i+1} successfully")
                except Exception as e:
                    self.logger.error(f"AI response error for section {i+1}: {e}")
            
            # Add Wikipedia as supplementary info
            wiki_info = ""
            try:
                self.logger.debug("Adding Wikipedia supplement...")
                wiki_summary = wikipedia.summary(topic, sentences=3)
                wiki_info = f"\n\nSupplementary Wikipedia Information:\n{wiki_summary}"
            except Exception as e:
                self.logger.warning(f"Wikipedia supplement error: {e}")
            
            # Combine all information
            if ai_responses:
                combined_info = f"Advanced AI Generated Information about {topic}:\n\n" + "\n\n".join(ai_responses) + wiki_info
                self.logger.info("AI information generated successfully")
            else:
                combined_info = f"Topic: {topic}\n\nI apologize, but AI couldn't generate detailed information at this time.{wiki_info}"
            
            # Save to file
            filename = self.save_and_open_notepad(topic, combined_info)
            if filename:
                return f"I've used advanced Gemini AI to generate detailed information about {topic} and saved it to your text editor."
            else:
                return f"AI generated information about {topic}, but couldn't save it to a file."
                
        except Exception as e:
            self.logger.error(f"Tell me about error: {e}")
            return "I encountered an error while generating information. Please try again."

    def save_and_open_notepad(self, topic, content):
        """Save content to file and open with notepad"""
        try:
            # Create filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = re.sub(r'[^\w\s-]', '', topic).strip()
            safe_topic = re.sub(r'[-\s]+', '_', safe_topic)[:30]
            filename = f"NOAH_Gemini_Info_{safe_topic}_{timestamp}.txt"
            
            # Try to save in Documents folder or current directory
            filepath = filename
            try:
                if platform.system() == "Windows":
                    documents_path = Path.home() / "Documents"
                    if documents_path.exists():
                        filepath = documents_path / filename
                else:
                    home_path = Path.home()
                    filepath = home_path / filename
            except Exception as e:
                self.logger.warning(f"Could not determine documents path: {e}")
            
            # Prepare content with header
            full_content = f"""
===============================================================
NOAH AI Assistant - Advanced Information Report (Powered by Google Gemini)
===============================================================
Topic: {topic}
Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
AI Model: {self.chatbot.get_model_info()}
Configuration: Loaded from config.py
===============================================================

{content}

===============================================================
Generated by NOAH AI Assistant - Powered by Google Gemini
Configuration loaded from config.py
For more information, say "tell me about [any topic]"
===============================================================
""".strip()
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            self.logger.info(f"Information saved to: {filepath}")
            
            # Open with appropriate editor
            try:
                if platform.system() == "Windows":
                    subprocess.Popen(['notepad.exe', str(filepath)])
                    self.logger.debug("Opened in Notepad")
                elif platform.system() == "Darwin":
                    subprocess.Popen(['open', '-t', str(filepath)])
                    self.logger.debug("Opened in TextEdit")
                else:
                    try:
                        subprocess.Popen(['gedit', str(filepath)])
                        self.logger.debug("Opened in gedit")
                    except FileNotFoundError:
                        try:
                            subprocess.Popen(['xdg-open', str(filepath)])
                            self.logger.debug("Opened with default editor")
                        except FileNotFoundError:
                            self.logger.info(f"File saved at: {filepath}. Please open manually.")
            except Exception as e:
                self.logger.warning(f"Could not open text editor: {e}")
            
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error saving/opening file: {e}")
            return None

    def process_command(self, query):
        """Process voice commands with enhanced error handling"""
        if not query:
            return
        
        self.logger.info(f"Processing command: {query}")
        
        try:
            # AI Writing/Information Generation Commands
            tell_me_patterns = [
                "tell me about", "what is", "explain", "describe",
                "information about", "write about", "generate information about"
            ]
            
            if any(pattern in query.lower() for pattern in tell_me_patterns):
                response = self.handle_tell_me_about(query)
                self.say(response)
                return

            # AI Model Loading Commands
            if any(phrase in query for phrase in ["load ai model", "initialize ai", "use gemini", "load gemini"]):
                self.initialize_ai_model()
                return

            # Configuration Status
            if "config status" in query or "api status" in query:
                status = self.chatbot.get_api_status()
                model_info = self.chatbot.get_model_info()
                self.say(f"Configuration status: {status}. Model: {model_info}")
                return

            # Switch input mode
            if "text mode" in query or "switch to text" in query:
                self.text_mode = True
                self.say("Switched to text input mode")
                return
            elif "voice mode" in query or "switch to voice" in query:
                if self.microphone:
                    self.text_mode = False
                    self.say("Switched to voice input mode")
                else:
                    self.say("Voice mode is not available. Microphone not detected.")
                return

            # Greeting Commands
            if any(word in query for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
                greetings = [
                        f"Hello {self.user_name}! How can I help you today?",
                        f"Hi there! I'm NOAH, ready to assist you with intelligent responses.",
                        f"Greetings {self.user_name}! What can I do for you today?",
                            ]

                self.say(random.choice(greetings))

            # Time Queries
            elif "time" in query:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                self.say(f"The current time is {current_time}")

            # Date Queries
            elif "date" in query or "today" in query:
                current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
                self.say(f"Today is {current_date}")

            # Weather Queries
            elif "weather" in query:
                city = DEFAULT_CITY  # Use city from config
                words = query.split()
                if "in" in words:
                    try:
                        in_index = words.index("in")
                        if in_index + 1 < len(words):
                            city = " ".join(words[in_index + 1:])
                    except:
                        pass
                weather = self.get_free_weather(city)
                self.say(f"Weather in {city}: {weather}")

            # Wikipedia Searches
            elif "wikipedia" in query or "search wikipedia" in query:
                search_query = query.replace("wikipedia", "").replace("search", "").strip()
                if search_query:
                    result = self.smart_search(search_query, "wikipedia")
                    self.say(result)
                    wiki_result = self.search_wikipedia(search_query)
                    if len(wiki_result) < 200:
                        self.say(wiki_result)
                else:
                    self.say("What would you like me to search on Wikipedia?")

            # Joke Requests
            elif "joke" in query or "funny" in query or "humor" in query:
                joke = self.tell_joke()
                self.say(joke)

            # System Information
            elif "system" in query or "status" in query or "performance" in query:
                info = self.get_system_info()
                self.say(info)

            # Screenshot
            elif "screenshot" in query or "screen capture" in query:
                result = self.take_screenshot()
                self.say(result)

            # Camera
            elif "camera" in query or "video" in query:
                self.say("Opening camera. Press Q to close.")
                result = self.open_camera()
                self.say(result)

            # ⭐ ENHANCED WEB SEARCHES - ALL PLATFORMS ⭐
            elif "search" in query:
                search_query = query.replace("search", "").strip()
                platform_detected = "google"
                
                # Detect platform in query
                if "youtube" in query or "video" in query:
                    platform_detected = "youtube"
                    search_query = search_query.replace("youtube", "").replace("video", "").strip()
                elif "amazon" in query or "buy" in query or "shop" in query:
                    platform_detected = "amazon"
                    search_query = search_query.replace("amazon", "").replace("buy", "").replace("shop", "").strip()
                elif "github" in query or "code" in query:
                    platform_detected = "github"
                    search_query = search_query.replace("github", "").replace("code", "").strip()
                
                if search_query:
                    result = self.smart_search(search_query, platform_detected)
                    self.say(result)
                else:
                    self.say("What would you like me to search for?")

            # ⭐ DIRECT YOUTUBE SEARCHES ⭐
            elif "youtube" in query:
                search_query = query.replace("youtube", "").replace("search", "").replace("on", "").strip()
                if search_query:
                    result = self.smart_search(search_query, "youtube")
                    self.say(result)
                else:
                    self.say("What would you like me to search on YouTube?")
                    
            # ⭐ DIRECT GOOGLE SEARCHES ⭐
            elif "google" in query and "search" in query:
                search_query = query.replace("google", "").replace("search", "").replace("on", "").strip()
                if search_query:
                    result = self.smart_search(search_query, "google")
                    self.say(result)
                else:
                    self.say("What would you like me to search on Google?")

            # Open Applications
            elif "open" in query:
                if "notepad" in query:
                    self.open_application("notepad")
                elif "calculator" in query:
                    self.open_application("calc")
                elif "browser" in query or "chrome" in query:
                    self.open_application("browser")
                else:
                    self.say("Which application would you like me to open?")

            # User Name Setting
            elif "my name is" in query or "call me" in query:
                words = query.split()
                try:
                    if "my name is" in query:
                        name_index = words.index("is") + 1
                    elif "call me" in query:
                        name_index = words.index("me") + 1
                    
                    new_name = " ".join(words[name_index:])
                    if new_name:
                        self.user_name = new_name.title()
                        self.user_data["name"] = self.user_name
                        self.save_user_data()
                        self.say(f"Nice to meet you, {self.user_name}!")
                except:
                    self.say("I didn't catch your name. Please try again.")

            # Help Command
            elif "help" in query or "commands" in query:
                help_text = f"""I can help you with many things! Here are some examples:

AI Features (Powered by Google Gemini from config.py):
• Say 'tell me about Python' for detailed AI-generated information
• Ask any question for intelligent responses
• Have natural conversations with advanced AI

Configuration Commands:
• Say 'config status' to check API key status
• Say 'load ai model' to initialize Gemini

🔍 WEB SEARCH FEATURES:
• Say 'search machine learning' - Google search
• Say 'youtube python tutorials' - YouTube search  
• Say 'search python on github' - GitHub search
• Say 'search laptop on amazon' - Amazon search
• Say 'search einstein on wikipedia' - Wikipedia search

System Features:
• Ask for time, date, or weather updates (default city: {DEFAULT_CITY})
• Request screenshots or camera access
• Get system performance information

Other Commands:
• Tell jokes and get entertainment
• Say 'text mode' to switch input methods
• Say 'exit' when you're done

Note: All AI responses are powered by Google Gemini with settings from config.py!"""
                
                self.say(help_text)

            # Exit Commands
            elif any(word in query for word in ["exit", "quit", "goodbye", "bye", "stop"]):
                self.say(f"Goodbye {self.user_name}! It was great helping you today with Google Gemini AI from config!")
                self.logger.info("NOAH AI Assistant session ended by user")
                self.is_listening = False

            # General AI Conversation with Gemini
            else:
                # If AI model is loaded, use Gemini for general conversation
                if self.ai_model_loaded:
                    try:
                        response = self.chatbot.get_response(query)
                        # Limit response length for speech
                        if len(response) > 200:
                            response = response[:200] + "... Would you like me to elaborate on any part?"
                        self.say(response)
                    except Exception as e:
                        self.logger.error(f"AI conversation error: {e}")
                        self.say("I didn't understand that. Try asking about a specific topic or say 'help' for commands.")
                else:
                    suggestions = [
                        "I didn't understand that command. Say 'load ai model' to enable advanced AI responses!",
                        "Sorry, I didn't catch that. Make sure your API key is set in config.py, then try 'load ai model'.",
                        "I'm not sure what you mean. Try searching: 'youtube music videos' or 'search python tutorials'."
                    ]
                    self.say(random.choice(suggestions))

        except Exception as e:
            self.logger.error(f"Command processing error: {e}")
            self.say("I encountered an error processing that command. Please try again.")

    # Utility Methods
    def get_free_weather(self, city="Mumbai"):
        """Get weather using free web scraping"""
        try:
            url = f"http://wttr.in/{city}?format=3"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.text.strip()
            else:
                return "Weather information not available"
        except Exception as e:
            self.logger.error(f"Weather error: {e}")
            return "Could not get weather information"

    def search_wikipedia(self, query):
        """Search Wikipedia"""
        try:
            result = wikipedia.summary(query, sentences=3)
            return result
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple results found for {query}. Please be more specific."
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for {query}"
        except Exception as e:
            self.logger.error(f"Wikipedia error: {e}")
            return "Could not access Wikipedia at this time"

    def tell_joke(self):
        """Tell jokes"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my wife she was drawing her eyebrows too high. She seemed surprised.",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "I'm reading a book about anti-gravity. It's impossible to put down!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't programmers like nature? It has too many bugs!"
        ]
        
        try:
            joke = pyjokes.get_joke()
            return joke
        except:
            return random.choice(jokes)

    def get_system_info(self):
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            info = f"System Status: CPU usage is {cpu_percent}%, Memory usage is {memory.percent}%, Disk usage is {disk.percent}%"
            
            try:
                battery = psutil.sensors_battery()
                if battery:
                    info += f", Battery is at {battery.percent}%"
            except:
                pass
            
            return info
        except Exception as e:
            self.logger.error(f"System info error: {e}")
            return "Could not retrieve system information"

    def take_screenshot(self):
        """Take a screenshot"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            # Try to save in Pictures folder
            filepath = filename
            try:
                if platform.system() == "Windows":
                    pictures_path = Path.home() / "Pictures"
                    if pictures_path.exists():
                        filepath = pictures_path / filename
            except:
                pass
            
            pyautogui.screenshot(str(filepath))
            self.logger.info(f"Screenshot saved: {filepath}")
            return f"Screenshot saved as {Path(filepath).name}"
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            return f"Could not take screenshot: {str(e)}"

    def open_camera(self):
        """Open camera"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "Could not access camera"
            
            self.logger.info("Camera opened - Press Q to close")
            while True:
                ret, frame = cap.read()
                if ret:
                    cv2.imshow('NOAH Camera - Press Q to close', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            self.logger.info("Camera closed")
            return "Camera closed"
        except Exception as e:
            self.logger.error(f"Camera error: {e}")
            return f"Could not open camera: {str(e)}"

    def open_application(self, app_name):
        """Open applications"""
        try:
            if platform.system() == "Windows":
                apps = {
                    "notepad": "notepad.exe",
                    "calc": "calc.exe",
                    "browser": "chrome.exe"
                }
                
                if app_name in apps:
                    subprocess.Popen([apps[app_name]])
                    self.say(f"Opening {app_name}")
                    self.logger.info(f"Opened {app_name}")
                elif app_name == "browser":
                    # Fallback: try to open default browser
                    webbrowser.open("https://www.google.com")
                    self.say("Opening default browser")
                    self.logger.info("Opened default browser")
                else:
                    self.say(f"I don't know how to open {app_name}")
            else:
                if app_name == "browser":
                    webbrowser.open("https://www.google.com")
                    self.say("Opening default browser")
                else:
                    self.say("Application opening is limited on this platform")
        except Exception as e:
            self.logger.error(f"App open error: {e}")
            self.say(f"Could not open {app_name}")

    def run(self):
        """Enhanced main execution loop"""
        print("🚀 Starting Enhanced NOAH AI Assistant with Google Gemini...")
        print(f"📁 Configuration loaded from config.py")
        print("🔍 All search features enabled: Google, YouTube, Amazon, GitHub, Wikipedia")
        print("="*60)
        
        # Check input method
        if self.text_mode:
            self.say(f"Hello {self.user_name}! Running in TEXT MODE for demo reliability.")
            print("📝 TEXT INPUT MODE: Type your commands instead of speaking")
        else:
            self.say(f"Hello {self.user_name}! I'm NOAH, your intelligent assistant.")
            self.say("Say 'tell me about' any topic for intelligent responses, or try 'youtube music videos' for search!")

        # Test microphone availability
        if not self.microphone and not self.text_mode:
            print("⚠️ No microphone detected. Assistant will run in text mode.")
            self.say("No microphone detected. Switching to text input mode.")
            self.text_mode = True

        while self.is_listening:
            try:
                query = self.get_input()
                if query:
                    self.process_command(query)
                time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n🛑 User interrupted")
                self.say("Shutting down NOAH Assistant. Goodbye!")
                self.logger.info("NOAH Assistant interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Runtime error: {e}")
                self.say("I encountered an error. Please try again.")

# Demo class and main function remain the same...
def main():
    print("🤖 Enhanced NOAH AI Assistant v5.0 - Powered by Google Gemini")
    print("📁 Configuration: Using config.py file")
    print("🔍 Full Search Support: Google, YouTube, Amazon, GitHub, Wikipedia")
    print("="*60)
    print("FEATURES:")
    print("✅ Google Gemini AI Integration (from config.py)")
    print("✅ Complete Web Search Suite")
    print("✅ YouTube Video Search")
    print("✅ Amazon Product Search") 
    print("✅ GitHub Code Search")
    print("✅ Wikipedia Knowledge Search")
    print("✅ Secure API key management")
    print("✅ Advanced Natural Language Processing")
    print("="*60)
    
    # Check if config file exists
    if not os.path.exists('config.py'):
        print("❌ ERROR: config.py file not found!")
        print("📝 Please create config.py with your API key:")
        print()
        print("# config.py")
        print('GEMINI_API_KEY = "your_actual_api_key_here"')
        print()
        print("🔗 Get your free API key from: https://aistudio.google.com")
        return

    print("\n🎤 Search Commands:")
    print("• 'youtube python tutorials' - Search YouTube")
    print("• 'search machine learning' - Search Google")
    print("• 'search laptop on amazon' - Search Amazon")
    print("• 'search react on github' - Search GitHub")
    print("• 'search einstein on wikipedia' - Search Wikipedia")
    print("\n🤖 AI Commands:")
    print("• 'load ai model' - Initialize Google Gemini from config")
    print("• 'tell me about [topic]' - AI generated information")
    print("• Ask any question for intelligent AI responses")
    print("• 'help' - Show all commands")
    print("• 'exit' - Quit")
    print("="*60)

    try:
        print("\n🚀 Starting NOAH Assistant...")
        assistant = AdvancedNOAHWithAI()
        assistant.run()

    except KeyboardInterrupt:
        print("\n👋 NOAH Assistant stopped by user.")
    except Exception as e:
        print(f"⚠️ Critical error: {e}")
        print("Please check your config.py file and API key setup.")

if __name__ == "__main__":
    main()
