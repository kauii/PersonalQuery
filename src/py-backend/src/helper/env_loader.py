import os
import sys
from dotenv import load_dotenv


def load_env():
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_path, '.env')
    load_dotenv(dotenv_path=env_path)
