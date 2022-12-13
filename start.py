import multiprocessing
import time

import send_request_order
from web_socket import Socket
from loguru_settings import log


process_dict: dict[str, dict[str, multiprocessing.Process]] = {}
WORK_SERVER = {}


def start_proc(symbols: list, user_data: dict, order_data: dict, _name: str):
    WORK_SERVER[_name] = True
    if _name in process_dict.keys():
        process_list = process_dict[_name]
    else:
        process_list = {}
    for s in symbols:
        if not WORK_SERVER[_name]:
            break
        send_request_order.close_all_position(user_data, order_data)
        order_data['symbol'] = s
        sock = Socket(user_data.copy(), order_data.copy())
        process = multiprocessing.Process(target=sock.start, args=())
        process_list[s] = process
        process_dict[_name] = process_list
        txt = 'Запуск процесса: ' + s
        print(txt)
        log.info(txt)
        process.start()

    while True:
        if not WORK_SERVER[_name]:
            break
        for symbol in symbols:
            if not WORK_SERVER[_name]:
                break
            process_list = process_dict[_name]
            if not process_list[symbol].is_alive():
                order_data['symbol'] = symbol
                sock = Socket(user_data.copy(), order_data.copy())
                process = multiprocessing.Process(target=sock.start, args=())
                process_list[symbol] = process
                process_dict[_name] = process_list
                txt = 'Перезапуск процесса: ' + s
                print(txt)
                log.info(txt)
                process.start()

        time.sleep(5)


def kill_all(_name):
    if not WORK_SERVER[_name]:
        process_list = process_dict[_name]
        for s in process_list.keys():
            process = process_list[s]
            if process.is_alive():
                txt = 'Килл процесса: ' + s
                print(txt)
                log.info(txt)
                process.kill()


def kill(_name):
    WORK_SERVER[_name] = False
    kill_all(_name)
    time.sleep(10)
    kill_all(_name)
