from pathlib import Path

from dumpdie import dd

dd(Path(__file__).parent.joinpath('config/database.py'))
