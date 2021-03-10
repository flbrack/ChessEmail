from dotenv import load_dotenv
from pathlib import Path
import os

# set path to env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    # Load in enviornemnt variables
    
    USERNAME = os.getenv('chessname')
	APITOKEN = os.getenv('lichess_api_token')
	EMAIL_ADDRESS = os.getenv('email')
	EMAIL_PASS = os.getenv('emailpass')