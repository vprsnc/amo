import json
from datetime import datetime
from loguru import logger



def timer_decorator(func):

     def timer(*args, **kwargs):
         start = datetime.now()
         logger.info(f'Starting timer at {start}')
         func(*args, **kwargs)
         end = datetime.now()
         logger.success(f'Ending timer at {end}, it took {end-start}.')

     return timer

def read_json(file):
     return json.loads('[' + file.read()[:-2] + ']')
