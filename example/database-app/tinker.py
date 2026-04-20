from dumpdie import dd
from fastapi_startkit.loader import Loader
params = Loader().get_parameters("config.database")

dd(params)
