import functools
import uuid
import inspect
import ast
import pickle

def remote(f):
    s=inspect.getsource(f)
    print(f'---\n{s}\n---')
    a=ast.parse(s)
    for x in ast.walk(a):
        print(a)
    x=pickle.dumps(a)
    print(x)
    y=pickle.loads(x)
    z = compile(y, '<remote>', 'exec')
    g=dict(__globals__=dict())
    l=dict()
    exec(z, g, l)
    print(g)
    print(l)
    def _runner(*a, **b):
        return exec
    return z

@remote
def name():
    return dict(_n=str(uuid.uuid4())[:8])

print(name())

@remote
def call(fn, *args):
    tmp = dict(_f=fn, _a=[])
    for a in args:
        if not isinstance(a, dict):
            tmp['_a'].append(dict(_v=a))
        else:
            tmp['_a'].append(a)
    return tmp
