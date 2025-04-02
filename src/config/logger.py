import os
import logging
from datetime import datetime

def logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    log_path = "logs"
    os.makedirs(log_path, exist_ok=True)
    filename=f'crawler-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.log'
    path = os.path.join(log_path, filename)
    
    file_handler = logging.FileHandler(path)
    file_handler.setFormatter(formatter)

    # stream_handler = logging.StreamHandler()
    # stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    # logger.addHandler(stream_handler)

    return logger