import re
import inspect

import redis
import functools
import pickle
from colorama import Fore
# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, db=0)


def cache_decorator(ignore_keys=None):
    if ignore_keys is None:
        ignore_keys = []

    def decorator(func):
        sig = inspect.signature(func)
        @functools.wraps(func)
        def wrapper(**kwargs):
            bound_args = sig.bind_partial(**kwargs)
            bound_args.apply_defaults()

            key = f'''{func.__name__}__{'__'.join([f'{k}={v}' for k, v in sorted(bound_args.arguments.items()) if k not in ignore_keys])}'''

            if (res := r.get(key)) is None:
                res = func(**kwargs)
                r.set(key, pickle.dumps(res))
                color = Fore.YELLOW
                log_title = 'save cache'
            else:
                res = pickle.loads(res)
                color = Fore.GREEN
                log_title = 'used cache'

            log_key = re.sub(r"(__)", f"{Fore.BLACK}\\1{Fore.RESET}", key)
            log_key = re.sub(r"(=)", f"{Fore.YELLOW}\\1{Fore.RESET}", log_key)
            print(f'''{color}[{log_title}] {f'len={len(res)}' if type(res) == list else ''}{Fore.RESET} {log_key}''')

            return res
        return wrapper
    return decorator
