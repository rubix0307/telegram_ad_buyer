import re
import inspect
import hashlib
import time

import redis
import functools
import pickle
from colorama import Fore


r = redis.Redis(host='localhost', port=6379, db=0)


def get_hash(text):
    my_bytes = text.encode()
    md5_hash = hashlib.md5(my_bytes)
    hash_hex = md5_hash.hexdigest()
    return hash_hex


def redis_cache(ignore_keys=None, ex=None, hash_use=False):
    if ignore_keys is None:
        ignore_keys = []

    def decorator(func):
        sig = inspect.signature(func)


        @functools.wraps(func)
        def wrapper(**kwargs):
            start_time = time.time()
            bound_args = sig.bind_partial(**kwargs)
            bound_args.apply_defaults()

            key = f'''{func.__name__}__{'__'.join([f'{k}={get_hash(str(v)) if hash_use else v}' for k, v in sorted(bound_args.arguments.items()) if k not in ignore_keys])}'''

            if (res := r.get(key)) is None:
                res = func(**kwargs)
                r.set(key, pickle.dumps(res), ex=ex)
                color = Fore.YELLOW
                log_title = 'save cache'
            else:
                res = pickle.loads(res)
                color = Fore.GREEN
                log_title = 'used cache'

            log_key = re.sub(r"(__)", f"{Fore.BLACK}\\1{Fore.RESET}", key)
            log_key = re.sub(r"(=)", f"{Fore.YELLOW}\\1{Fore.RESET}", log_key)

            duration = str(round(time.time() - start_time, 3)).ljust(7, '0')
            duration = f'{color if float(duration) < 3 else Fore.RED}{duration}s{Fore.RESET}'
            print(
                f'''{color}[{log_title}] {f'len={str(len(res)).rjust(3, str(0))}' if type(res) == list else ''} duration={duration} res={Fore.GREEN if bool(res) else ''}{bool(res)}{Fore.RESET} {log_key}''')

            return res
        return wrapper
    return decorator
