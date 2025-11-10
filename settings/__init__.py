from pathlib import Path
from dotenv import dotenv_values


ROOT_DIR = Path(__file__).resolve().parent.parent
env = dict(dotenv_values())
