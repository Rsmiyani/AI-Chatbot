import warnings
import os
import google.generativeai as genai

warnings.filterwarnings('ignore')

# Try to import config file
try:
    from config import GEMINI_API_KEY as CONFIG_API_KEY, GEMINI_MODEL, MAX_OUTPUT_TOKENS, TEMPERATURE
except ImportError:
    print("⚠️ Config file not found. Please create config.py with your API key.")
    CONFIG_API_KEY = None
    GEMINI_MODEL = "gemini-1.5-flash"
    MAX_OUTPUT_TOKENS = 1000
    TEMPERATURE = 0.7

class EnhancedChatbot:
    def __init__(self):
        self.model_type = None
        self.gemini_model = None
        self.api_key = None

    def load_gemini_api(self, api_key=None):
        """Load Google Gemini API with config file support"""
        try:
            if api_key:
                self.api_key = api_key
            else:
                # Try multiple sources for API key (priority order)
                self.api_key = (
                    os.getenv('GEMINI_API_KEY') or  # Environment variable (highest priority)
                    CONFIG_API_KEY or               # Config file (second priority)
                    None
                )
                
            if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
                print("❌ No valid API key found!")
                print("📝 Please update config.py with your actual Gemini API key")
                print("🔗 Get your free key from: https://aistudio.google.com")
                print("\n💡 Edit config.py and replace 'YOUR_API_KEY_HERE' with your real API key")
                return False
            
            print("Loading Google Gemini from configuration...")
            genai.configure(api_key=self.api_key)
            
            # Initialize Gemini model with config settings
            self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
            self.model_type = "gemini"
            print(f"✅ Google Gemini ({GEMINI_MODEL}) loaded successfully from config!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading Gemini: {str(e)}")
            if "API_KEY" in str(e).upper() or "authentication" in str(e).lower():
                print("🔑 API Key Error: Please check your API key in config.py")
                print("   Make sure it's valid and hasn't expired")
            elif "not found" in str(e).lower():
                print("📁 Config Error: Make sure config.py exists in the same folder")
            return False

    def generate_gemini_response(self, message, chat_history=None):
        """Generate response using Google Gemini with config settings"""
        try:
            # Build conversation context for better responses
            prompt = "You are NOAH, an intelligent AI assistant created to help users with various tasks. Please provide helpful, informative, and conversational responses. Be friendly and professional.\n\n"
            
            if chat_history and len(chat_history) > 0:
                # Add recent conversation history
                prompt += "Previous conversation:\n"
                for msg in chat_history[-5:]:  # Last 5 messages
                    if msg.get('role') == 'user':
                        prompt += f"User: {msg.get('content', '')}\n"
                    elif msg.get('role') == 'assistant':
                        prompt += f"NOAH: {msg.get('content', '')}\n"
                prompt += "\n"
            
            # Add current message
            prompt += f"User: {message}\nNOAH:"
            
            # Generate response with config settings
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=TEMPERATURE,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                    top_p=0.8,
                    top_k=40
                )
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I'm having trouble generating a response right now. Please try again."
                
        except Exception as e:
            print(f"Gemini generation error: {e}")
            if "API_KEY" in str(e).upper():
                return "Please check your Gemini API key in config.py. It seems to be invalid or expired."
            elif "quota" in str(e).lower() or "limit" in str(e).lower():
                return "API quota exceeded. Please check your Gemini API usage limits."
            elif "blocked" in str(e).lower() or "safety" in str(e).lower():
                return "Sorry, I cannot respond to that request due to safety filters. Please try asking something else."
            else:
                return "I encountered an error with Gemini. Please try again in a moment."

    def get_response(self, message, chat_history=None):
        """Main method to get response using Gemini"""
        try:
            if self.model_type == "gemini" and self.gemini_model:
                return self.generate_gemini_response(message, chat_history)
            else:
                return "Please load Gemini model first by saying 'load ai model' or 'use gemini'."
        except Exception as e:
            print(f"Response generation error: {e}")
            return "I'm having trouble generating a response. Please try again."

    def is_model_loaded(self):
        """Check if Gemini model is loaded"""
        return self.model_type == "gemini" and self.gemini_model is not None

    def get_model_info(self):
        """Get information about the currently loaded model"""
        if self.model_type == "gemini":
            return f"Google {GEMINI_MODEL} - Advanced AI Assistant (from config)"
        else:
            return "No model loaded"

    def get_api_status(self):
        """Get API configuration status"""
        if CONFIG_API_KEY and CONFIG_API_KEY != "YOUR_API_KEY_HERE":
            return "✅ API key configured in config.py"
        elif os.getenv('GEMINI_API_KEY'):
            return "✅ API key found in environment variables"
        else:
            return "❌ No API key configured"
import warnings
import os
import google.generativeai as genai

warnings.filterwarnings('ignore')

# Try to import config file
try:
    from config import GEMINI_API_KEY as CONFIG_API_KEY, GEMINI_MODEL, MAX_OUTPUT_TOKENS, TEMPERATURE
except ImportError:
    print("⚠️ Config file not found. Please create config.py with your API key.")
    CONFIG_API_KEY = None
    GEMINI_MODEL = "gemini-1.5-flash"
    MAX_OUTPUT_TOKENS = 150
    TEMPERATURE = 0.25

class EnhancedChatbot:
    def __init__(self):
        self.model_type = None
        self.gemini_model = None
        self.api_key = None
        self.concise_mode = True  # New: Toggle for ultra-concise responses

    def load_gemini_api(self, api_key=None):
        """Load Google Gemini API with config file support"""
        try:
            if api_key:
                self.api_key = api_key
            else:
                # Try multiple sources for API key (priority order)
                self.api_key = (
                    os.getenv('GEMINI_API_KEY') or  # Environment variable (highest priority)
                    CONFIG_API_KEY or              # Config file (second priority)
                    None
                )

            if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
                print("❌ No valid API key found!")
                print("📝 Please update config.py with your actual Gemini API key")
                print("🔗 Get your free key from: https://aistudio.google.com")
                print("\n💡 Edit config.py and replace 'YOUR_API_KEY_HERE' with your real API key")
                return False

            print("Loading Google Gemini from configuration...")
            genai.configure(api_key=self.api_key)

            # Initialize Gemini model with config settings
            self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
            self.model_type = "gemini"
            print(f"✅ Google Gemini ({GEMINI_MODEL}) loaded successfully from config!")
            return True

        except Exception as e:
            print(f"❌ Error loading Gemini: {str(e)}")
            if "API_KEY" in str(e).upper() or "authentication" in str(e).lower():
                print("🔑 API Key Error: Please check your API key in config.py")
                print("   Make sure it's valid and hasn't expired")
            elif "not found" in str(e).lower():
                print("📁 Config Error: Make sure config.py exists in the same folder")
            return False

    def generate_gemini_response(self, message, chat_history=None):
        """Generate concise, stable response using Google Gemini with strict style control"""
        try:
            # System instruction for consistent, concise responses
            system_instruction = (
                "You are NOAH, a helpful AI assistant. Follow these rules strictly:\n"
                "- Keep responses under 120 words\n"
                "- Be direct and actionable\n"
                "- Use bullet points for lists (max 3 bullets)\n"
                "- Give numbered steps for procedures\n"
                "- Avoid filler words and repetition\n"
                "- Don't add unnecessary disclaimers\n"
                "- If unclear, give most likely answer + 1 clarification"
            )

            # Build compact conversation history (last 3 exchanges only)
            history_context = ""
            if chat_history and len(chat_history) > 0:
                recent_messages = []
                for msg in chat_history[-6:]:  # Last 6 messages = 3 exchanges
                    role = msg.get('role', 'user')
                    content = msg.get('content', '').strip()
                    if content:
                        if role == 'user':
                            recent_messages.append(f"User: {content}")
                        elif role == 'assistant':
                            recent_messages.append(f"NOAH: {content}")
                
                if recent_messages:
                    history_context = "Recent context:\n" + "\n".join(recent_messages) + "\n\n"

            # Apply concise mode if enabled
            style_modifier = ""
            if self.concise_mode:
                style_modifier = "ULTRA-CONCISE MODE: Maximum 3 sentences. No elaboration unless critical.\n"

            # Compose the final prompt
            final_prompt = (
                f"{system_instruction}\n\n"
                f"{style_modifier}"
                f"{history_context}"
                f"Current question: {message}\n\n"
                f"Provide a concise, helpful response:"
            )

            # Generate with strict parameters for consistency
            response = self.gemini_model.generate_content(
                final_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=TEMPERATURE,        # From config (0.25 recommended)
                    max_output_tokens=MAX_OUTPUT_TOKENS,  # From config (150 recommended)
                    top_p=0.7,                      # Focused sampling
                    top_k=20,                       # Limited vocabulary choices
                    candidate_count=1               # Single response
                )
            )

            if response and response.text:
                # Clean and validate response
                clean_response = response.text.strip()
                
                # Hard limit for voice output (prevent extremely long responses)
                if len(clean_response) > 800:
                    clean_response = clean_response[:800] + "..."
                
                # Remove any remaining "NOAH:" prefixes that might appear
                if clean_response.startswith("NOAH:"):
                    clean_response = clean_response[5:].strip()
                    
                return clean_response
            else:
                return "I'm having trouble generating a response right now. Please try again."

        except Exception as e:
            print(f"Gemini generation error: {e}")
            
            # Specific error handling
            error_msg = str(e).upper()
            if "API_KEY" in error_msg or "AUTHENTICATION" in error_msg:
                return "API key error. Please check your Gemini API key in config.py."
            elif "QUOTA" in error_msg or "LIMIT" in error_msg:
                return "API quota exceeded. Please check your usage limits."
            elif "BLOCKED" in error_msg or "SAFETY" in error_msg:
                return "Sorry, I cannot respond to that request due to safety filters."
            elif "NETWORK" in error_msg or "CONNECTION" in error_msg:
                return "Network error. Please check your internet connection."
            else:
                return "I encountered an error. Please try again in a moment."

    def get_response(self, message, chat_history=None):
        """Main method to get response using Gemini"""
        try:
            if self.model_type == "gemini" and self.gemini_model:
                return self.generate_gemini_response(message, chat_history)
            else:
                return "Please load Gemini model first by saying 'load ai model' or 'use gemini'."
        except Exception as e:
            print(f"Response generation error: {e}")
            return "I'm having trouble generating a response. Please try again."

    def is_model_loaded(self):
        """Check if Gemini model is loaded"""
        return self.model_type == "gemini" and self.gemini_model is not None

    def get_model_info(self):
        """Get information about the currently loaded model"""
        if self.model_type == "gemini":
            return f"Google {GEMINI_MODEL} - Advanced AI Assistant (from config)"
        else:
            return "No model loaded"

    def get_api_status(self):
        """Get API configuration status"""
        if CONFIG_API_KEY and CONFIG_API_KEY != "YOUR_API_KEY_HERE":
            return "✅ API key configured in config.py"
        elif os.getenv('GEMINI_API_KEY'):
            return "✅ API key found in environment variables"
        else:
            return "❌ No API key configured"

    def toggle_concise_mode(self):
        """Toggle between normal and ultra-concise response modes"""
        self.concise_mode = not self.concise_mode
        mode_status = "ON" if self.concise_mode else "OFF"
        return f"Concise mode is now {mode_status}"

    def set_concise_mode(self, enabled=True):
        """Explicitly set concise mode on or off"""
        self.concise_mode = enabled
        mode_status = "enabled" if enabled else "disabled"
        return f"Concise mode {mode_status}"
