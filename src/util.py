import logging
from functools import wraps
from time import time
from urllib.parse import urljoin

from requests import post
from requests.exceptions import ConnectionError

from src import env


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


def notify_callback(callback_url, status, data):
    headers = {"Authorization": f"Bearer {env.WALLY_BEARER}"}
    payload = {"status_code": status, "data": data}
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
