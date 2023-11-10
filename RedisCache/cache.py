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


def get_cache_key(func, ignore_keys: list = [], hash_use=False, **kwargs):
    sig = inspect.signature(func)
    bound_args = sig.bind_partial()
    bound_args.apply_defaults()

    all_args = {}
    all_args.update(**kwargs)
    all_args.update(bound_args.arguments.items())

    key = f'''{func.__name__}__{'__'.join([f'{k}={get_hash(str(v)) if hash_use else v}'
                                           for k, v in sorted(all_args.items())
                                           if k not in ignore_keys])}'''
    return key

def get_cache(cache_key):
    return r.get(cache_key)

def redis_cache(ignore_keys=None, ex=None, hash_use=False):
    if ignore_keys is None:
        ignore_keys = []

    def decorator(func):

        @functools.wraps(func)
        def wrapper(**kwargs):
            start_time = time.time()

            key = get_cache_key(func, ignore_keys=ignore_keys, hash_use=hash_use, **kwargs)
            cache_value = get_cache(key)

            if cache_value is None:
                res = func(**kwargs)
                r.set(key, pickle.dumps(res), ex=ex)
                color = Fore.YELLOW
                log_title = 'save cache'
            else:
                res = pickle.loads(cache_value)
                color = Fore.GREEN
                log_title = 'used cache'

            log_key = re.sub(r"(__)", f"{Fore.BLACK}\\1{Fore.RESET}", key)
            log_key = re.sub(r"(=)", f"{Fore.YELLOW}\\1{Fore.RESET}", log_key)

            duration = str(round(time.time() - start_time, 3)).ljust(7, '0')
            duration = f'{color if float(duration) < 3 else Fore.RED}{duration}s{Fore.RESET}'

            try:
                print(
                    f'''{color}[{log_title}] {f'len={str(len(res)).rjust(3, str(0))}' if type(res) == list else ''} duration={duration} res={Fore.GREEN if bool(res) else ''}{bool(res)}{Fore.RESET} {log_key}''')
            except UnicodeEncodeError:
                pass

            return res

        return wrapper
    return decorator
