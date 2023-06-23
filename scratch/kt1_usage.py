import kt1
import time
import structlog

r = kt1.repository("demo1.db")
r.add(dict(current_time=time.time()))

l = structlog.get_logger()


class users(kt1.cqrs):

    def init(self):
        self.users = {}

    def handle_create_user(self, username, password=None, **rest):
        l.info('handle_create_user', username=username, password=password, **rest)
        if username not in self.users:
            self.users[username] = password
            return True
        else:
            return False

    def handle_delete_user(self, username=None, **rest):
        l.info('handle_delete_user', username=username, **rest)
        if username in self.users:
            del self.users[username]
            return True
        else:
            return False

    def list_users(self):
        return list(self.users)


x = users(r)
print('list_users:', x.list_users())
x.create_user(username='daisy', password='pretty')
x.create_user(username='donald', password='secret')
print('list_users:', x.list_users())
r.add(dict(state=x.list_users()))
x.create_user(username='dagobert', password='gold')
print('list_users:', x.list_users())
x.delete_user(username='donald')
print('list_users:', x.list_users())
x.delete_user(username='dagobert')
print('list_users:', x.list_users())

import random

pos = r.add(random.random())
r.add(random.random())
r.add(random.random())
for a in r.since(pos):
    print(a)
