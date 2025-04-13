import os
from dotenv import load_dotenv
import loguru
import sys

load_dotenv()


class Config:
    BACKEND_URL = os.getenv("BACKEND_URL")
    APP_NAME = "TightGroups"
    VERSION = "0.9.11"


logger = loguru.logger
logger.add("./asf_mount_point/app_storage/logs/front_logs.log")
logger.add(sys.stdout)
