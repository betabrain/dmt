
if __name__ == "__main__":
    import form
    import attr

    @attr.s(slots=True)
    class User(form.Form):
        username = attr.ib()
        password = attr.ib()

    u1 = form.tk(User)

    url = form.web1(User)
    print(url)
    u2 = form.web2(url)

    @form.with_url
    @attr.s(slots=True)
    class User(object):
        username = attr.ib()
        password = attr.ib()

    # https://localhost/__main__.User
    # => FORM
    # (submit) => https://localhost/23476179837912 (id)

    u1 = User("abc", "secret")  # DISALLOWED!!!
    url = u1.get_url()

    u2 = form.proxy(url)
    pw = u2.get_password()

    # two+ processes... object server, application(s)

    import form

    User = form.ns.User
    u = form.ns.User("abc", "def")
    print(u)
# form.Proxy('https://localhost/789273487263489827348')
