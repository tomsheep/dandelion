# -*- coding: utf-8 -*-
import web


class CookieStore(web.session.Store):
    """Store for saving session using cookie.

    TODO: Put your code here

    """
    def __init__(self, cookie_name):
        self.cookie_name = cookie_name
        

    def __contains__(self, key):
        cookies = web.cookies()
        return self.cookie_name in cookies

    def __getitem__(self, key):
        pickled = web.cookies().get(self.cookie_name)
        return self.decode(pickled)

    def __setitem__(self, key, value):
        pickled = self.encode(value)
        self._setcookie(pickled);

    def _setcookie(self, value, expires='', **kw):
        web.setcookie(self.cookie_name, value, expires=expires)

    def __delitem__(self, key):
        self._setcookie('', expires=-1);

    def cleanup(self, timeout):
        pass
