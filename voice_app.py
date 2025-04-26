
import speech_recognition as sr
import pyttsx3
import datetime
import sys
import random # Moved import to the top (best practice)
import time # Added for potential delays if needed
from typing import Union

# --- Constants (Optional but good practice) ---
LISTENING_TIMEOUT = 5 # seconds to wait for speech
PHRASE_TIME_LIMIT = 10 # max seconds for a phrase
AMBIENT_NOISE_DURATION = 0.5 # seconds to adjust for noise
PAUSE_THRESHOLD = 0.8 # seconds of non-speaking audio before phrase is considered complete (slightly lower might feel more responsive)

# --- Initialization ---
try:
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = PAUSE_THRESHOLD

    # Initialize the text-to-speech engine
    tts_engine = pyttsx3.init()
    # Optional: Adjust voice properties
    # voices = tts_engine.getProperty('voices')
    # tts_engine.setProperty('voice', voices[1].id) # Example: Set to the second voice
    # tts_engine.setProperty('rate', 180) # Speed percent
    # tts_engine.setProperty('volume', 1.0) # Volume 0-1

except ImportError as e:
    print(f"Error importing a required library: {e}")
    print("Please ensure SpeechRecognition, pyttsx3, and PyAudio (or platform equivalent) are installed.")
    sys.exit(1)
except Exception as e:
    print(f"Error initializing libraries: {e}")
    print("There might be an issue with your audio setup or library installation.")
    sys.exit(1)


# --- Helper Functions ---
def speak(text: str) -> None:
    """Converts text to speech."""
    print(f"AI: {text}")
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except RuntimeError as e:
        print(f"Error during speech synthesis (RuntimeError): {e}")
        print("This might happen if the engine is busy. Retrying might help.")
    except Exception as e:
        print(f"Error during speech synthesis: {e}")

def listen_for_command() -> str | None:
    """Listens for command via microphone and returns the recognized text (lowercase)."""
    with sr.Microphone() as source:
        print("\nListening...")
        # Adjust for ambient noise dynamically
        try:
             recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_NOISE_DURATION)
        except Exception as e:
             print(f"Warning: Could not adjust for ambient noise: {e}")
             # Continue anyway, might affect recognition quality

        try:
            # Listen for audio input
            audio = recognizer.listen(
                source,
                timeout=LISTENING_TIMEOUT,
                phrase_time_limit=PHRASE_TIME_LIMIT
            )
        except sr.WaitTimeoutError:
            print("No speech detected within the timeout period.")
            return None
        except Exception as e:
            print(f"Error capturing audio: {e}")
            return None

    # Recognize speech using Google Web Speech API
    try:
        print("Recognizing...")
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        # Don't speak here, just return None or maybe a silent indicator
        print("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        # Only speak if the TTS engine itself is likely working
        speak("Sorry, I'm having trouble connecting to the speech recognition service.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during recognition: {e}")
        return None

def process_command(command: str | None) -> str | None:
    """Processes the command and determines the response. Returns 'exit' to quit."""
    if command is None:
        return None # Do nothing if no command was understood

    # --- Simple Command Logic ---
    try: # Add a general try block for safety within processing
        if "hello" in command or "hi" in command or "hey" in command:
            speak("Hello there! How can I help you today?")
        elif "what time is it" in command or "current time" in command:
            now = datetime.datetime.now().strftime("%I:%M %p") # e.g., "03:30 PM"
            speak(f"The current time is {now}")
        elif "what is your name" in command:
            speak("I am a simple voice assistant based on Python.")
        elif "tell me a joke" in command:
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the scarecrow win an award? Because he was outstanding in his field!",
                "What do you call fake spaghetti? An impasta!",
                "Why did the bicycle fall over? Because it was two tired!",
            ]
            if jokes: # Make sure the list is not empty
                 speak(random.choice(jokes))
            else:
                 speak("I'm out of jokes right now!")
        elif "goodbye" in command or "exit" in command or "quit" in command or "stop" in command:
            speak("Goodbye! Have a great day.")
            return "exit" # Signal to exit the main loop
        else:
            # Default response if command is not recognized
            speak("Sorry, I didn't quite catch that. Could you please repeat?")

    except Exception as e:
        print(f"An error occurred while processing the command: {e}")
        speak("Oops, something went wrong while processing your request.")

    return None # Indicate not to exit by default

# --- Main Loop ---
if __name__ == "__main__":
    speak("Voice assistant activated. How can I assist you?")
    while True:
        try:
            command = listen_for_command()
            exit_signal = process_command(command)
            if exit_signal == "exit":
                break # Exit the loop if process_command signals to
        except KeyboardInterrupt:
             print("\nExiting program via Keyboard Interrupt.")
             speak("Shutting down.")
             break
        except Exception as e:
             print(f"\nAn unexpected error occurred in the main loop: {e}")
             speak("An unexpected error occurred. Please restart me.")
             # Optional: add a small delay before trying again or break
             # time.sleep(2)
             break # Or continue if you want it to try recovering

    print("Program terminated.")
