import apsw
import contextlib
import functools
import inspect
import re

# frozendict implementation inspired by
# https://www.python.org/dev/peps/pep-0351/
#


class frozendict(dict):

    def __hash__(self):
        return id(self)

    def __getattribute__(self, key):
        if key in self:
            return self[key]

        return dict.__getattribute__(self, key)

    def _immutable(self, *args, **kws):
        raise TypeError("object is immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable
    pop = _immutable
    popitem = _immutable


def db(*, filename=":memory:"):
    dbc = apsw.Connection(filename)

    def _sqlfunc(dbc, *, single=False):

        def _decorator(func):
            assert hasattr(func, "__doc__")
            assert isinstance(func.__doc__, str)
            signature = inspect.signature(func)

            @functools.wraps(func)
            def _wrapper(*args, **kwargs):
                bindings = signature.bind(*args, **kwargs)
                bindings.apply_defaults()
                bindings = dict(bindings.arguments)
                bindings.update(func(*args, **kwargs) or {})
                answer = None
                with contextlib.closing(dbc.cursor()) as cursor:
                    cursor.execute(func.__doc__, bindings)
                    try:
                        if single:
                            answer = cursor.fetchone()[0]
                        else:
                            keys = [
                                "_".join(re.findall("\w[\w\d]+", attr[0]))
                                for attr in cursor.getdescription()
                            ]
                            answer = list(
                                map(
                                    lambda vals: frozendict(zip(keys, vals)),
                                    cursor.fetchall(),
                                )
                            )
                    except apsw.ExecutionCompleteError:
                        pass
                return answer

            return _wrapper

        return _decorator

    return functools.partial(_sqlfunc, dbc)


if __name__ == "__main__":
    import roxy

    sql = roxy.db()

    @sql()
    def setup():
        """
        create table user (username, password);
        create table login (username, timestamp text default current_timestamp);
        """

    setup()

    @sql()
    def create_user(username):
        """
        insert into user values (:username, :password)
        """
        return dict(password="secret")

    @sql(single=True)
    def num_users():
        """ select count(*) from user; """

    while num_users() < 10:
        create_user(f"user_{num_users()}")

    @sql()
    def login(username, password):
        """
        insert into login (username) values (:username);
        select username from user where
            username is :username and
            password is :password;
        """

    if login("user_4", "bad pw"):
        print("success")
    else:
        print("login failed")

    if login("user_4", "secret"):
        print("success")
    else:
        print("login failed")

    if login("user_7", "secret"):
        print("success")
    else:
        print("login failed")

    @sql()
    def logins_per_user():
        """
        select username, count(timestamp) as num_logins, max(timestamp) as last_login
        from user join login using (username)
        group by username
        """

    for r in logins_per_user():
        print(
            f"{r.username} logged in {r.num_logins} times, last time at {r.last_login}"
        )
