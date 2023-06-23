import functools
import uuid
import concurrent.futures

def send(tup):
    (uid, fn, args, kwargs, fut) = tup
    print(uid, args, kwargs)
    fut.set_result(fn(*args, **kwargs))

def remote(fn):
    @functools.wraps(fn)
    def _fn(*args, **kwargs):
        fut = concurrent.futures.Future()
        send((uuid.uuid4(), fn, args, kwargs, fut))
        return fut.result()
    _fn.remote_id = uuid.uuid4()
    return _fn

@remote
def thread(*fns):
    def _fn(*args, **kwargs):
        obj = fns[0](*args, **kwargs)
        for fn in fns[1:]:
            obj = fn(obj)
            if isinstance(obj, concurrent.futures.Future):
                obj = obj.result()
        return obj
    return _fn

x = thread(
    remote(dict),
    remote(
        thread(
            remote(list),
            remote(len),
            remote(str),
        ),
    ),
    remote(print),
)

print(x)
x(abc=44, ghi=3.2)
