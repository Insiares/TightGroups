import os
from dotenv import load_dotenv
import loguru 
load_dotenv()

class Config:
    BACKEND_URL = os.getenv("BACKEND_URL")
    APP_NAME = "TightGroups"
    VERSION = "0.1.0"

    
logger = loguru.logger
logger.add("./logs/front_logs.log")
