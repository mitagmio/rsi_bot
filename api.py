import multiprocessing

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

import config_api as cf
from start import start_proc, kill
import threading

app = FastAPI()
process_dict: dict[str, multiprocessing.Process] = {}


def start_server():
    uvicorn.run(app, host=cf.host_url, port=cf.port)


def start_doing(*args):
    start_proc(*args)


class InputDataOn(BaseModel):
    name: str
    symbols: list
    user_data: dict
    order_data: dict


class InputDataOff(BaseModel):
    name: str


@app.post('/startup_bot')
def startup_bot(item: InputDataOn):
    process = threading.Thread(target=start_doing, args=(
        item.symbols, item.user_data, item.order_data, item.name))
    process.start()
    process_dict[item.name] = process
    return {'result': 'On'}


@app.post('/disable_bot')
def disable_bot(item: InputDataOff):
    threading.Thread(target=kill, args=[item.name]).start()
    return {'result': 'Off'}


if __name__ == '__main__':
    start_server()
