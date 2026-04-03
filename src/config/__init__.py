import os

from dotenv import load_dotenv

load_dotenv()

MODEL_BASE_URL = os.environ.get("MODEL_BASE_URL")
MODEL_PROVIDER = os.environ.get("MODEL_PROVIDER")
MODEL_NAME_DEFAULT = os.environ.get("MODEL_NAME_DEFAULT")
MODEL_NAME_PLANNER = os.environ.get("MODEL_NAME_PLANNER")
MODEL_NAME_CRITIC = os.environ.get("MODEL_NAME_CRITIC")
