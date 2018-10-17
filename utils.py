import ctypes
import inspect
from functools import wraps
from queue import Queue
from threading import Thread


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def timeout_func(time_limited):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):

            class TimeLimited(Thread):
                def __init__(self):
                    self.q = Queue()
                    Thread.__init__(self)

                def run(self):
                    res = func(*args, **kw)
                    self.q.put(res)

            t = TimeLimited()
            t.start()
            t.join(timeout=time_limited)
            if t.is_alive():
                stop_thread(t)
                raise TimeoutError('Function execution overtime')
            while not t.q.empty():
                return t.q.get()

        return wrapper

    return decorator


def print_yellow(content):
    print('\033[4;33m' + content + '\033[0m')


def print_blue(content):
    print('\033[1;34m' + content + '\033[0m')


def print_green(content):
    print('\033[1;32m' + content + '\033[0m')


def print_red(content):
    print('\033[1;31m' + content + '\033[0m')
