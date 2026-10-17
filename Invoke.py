from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv('OPENROUTER_API_KEY')  # Get the API key from the environment variable


