import asyncio
import logging
from functools import wraps
from time import time
from urllib.parse import urljoin

from requests import post
from requests.exceptions import ConnectionError

import src.logging_util as log_util
from src import env
from src.azure_queue import retrieve_messages


def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def log_execution_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time()
        result = await func(*args, **kwargs)
        end_time = time()
        execution_time = end_time - start_time
        logging.info(
            f"Function '{func.__name__}' took {execution_time:.4f} seconds to complete."
        )
        return result

    return wrapper


def process_messages(source):
    def decorator(func):
        @wraps(func)
        async def wrapper():
            try:
                messages = await retrieve_messages()
            except Exception as e:
                logging.error(f"Failed to retrieve messages: {e}")
                return
            if not len(messages):
                logging.info("No messages fetched")
                return

            errored = 0
            successful = 0

            for msg in messages:
                logging.info(f"Processing message: {msg}")
                if not (callback_url := msg.pop("callback_url")):
                    logging.info("No callback_url, not processing message")
                    continue
                try:
                    result = await func(**msg)
                    if result is None:
                        raise Exception("Result is None")
                    logging.info(f"result: {result[0:10]}")

                    notify_callback(
                        callback_url, status=200, source=source, data=result
                    )
                    successful += 1
                except Exception as e:
                    errored += 1
                    logging.error(f"process_messages Error: {e}")
                    if isinstance(e, TypeError):
                        notify_callback(
                            callback_url,
                            status=400,
                            source=source,
                            data=f"Type error: message doesn't contain correct info. {e}",
                        )
                    else:
                        notify_callback(
                            callback_url,
                            status=500,
                            source=source,
                            data="Internal server Error",
                        )

            logging.info(
                f"Processed {len(messages)} messages: {successful} success, {errored} err"
            )

        return wrapper

    return decorator


def notify_callback(callback_url, status, source, data):
    headers = {"Authorization": f"Bearer {env.WALLY_BEARER}"}
    payload = {"status_code": status, "source": source, "data": data}
    try:
        response = post(
            urljoin(env.WALLY_URL, callback_url),
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
    except ConnectionError as conn_err:
        logging.error(f"cannot connect to callback_url: {callback_url}")
    except Exception as e:
        logging.error(f"bad response from callback_url: {e}")


def main_setup(func):
    def wrapper(*args, **kwargs):
        log_util.setup()
        logging.info("Starting up")
        result = asyncio.run(func(*args, **kwargs))
        return result

    return wrapper
