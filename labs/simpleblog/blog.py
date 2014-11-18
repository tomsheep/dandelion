#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Basic blog using webpy 0.3 '''
import sys
sys.path.append("../../vendor/webpy")
import web
web.config.debug = False
import model
from functools import wraps
from config import DB_SETTINGS
from optparse import OptionParser
# Url mappings
urls = (
    '/', 'Index',
    '/view/(\d+)', 'View',
    '/new', 'New',
    '/delete/(\d+)', 'Delete',
    '/edit/(\d+)', 'Edit',
    '/login', 'Login',
    '/logout', 'Logout',
    )
# Templates
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'user': None})
t_globals = {'datestr': web.datestr, 'session': session}
render = web.template.render('templates', base='base', globals=t_globals)


def need_auth(f):
    @wraps(f)
    def _(*args, **kw):
        user = session.get('user')
        if not user:
            redir_url = web.ctx.homedomain + web.ctx.path
            url = '/login?redir=%s' % redir_url
            raise web.seeother(url)
        return f(*args, **kw)
    return _


class Index:

    def GET(self):
        ''' Show page '''

        posts = model.get_posts()
        return render.index(posts)


class View:

    def GET(self, id):
        ''' View single post '''

        post = model.get_post(int(id))
        return render.view(post)


class New:

    form = web.form.Form(web.form.Textbox('title', web.form.notnull,
                         size=30, description='Post title:'),
                         web.form.Textbox('subtitle',
                         size=30, description='Post sub-title:'),
                         web.form.Textarea('content', web.form.notnull,
                         rows=30, cols=80, description='Post content:'),
                         web.form.Button('Post entry'))

    @need_auth
    def GET(self):
        form = self.form()
        return render.new(form)

    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new(form)
        model.new_post(form.d.title, form.d.subtitle, form.d.content)
        raise web.seeother('/')


class Delete:

    def POST(self, id):
        model.del_post(int(id))
        raise web.seeother('/')


class Edit:

    def GET(self, id):
        post = model.get_post(int(id))
        form = New.form()
        form.fill(post)
        return render.edit(post, form)

    def POST(self, id):
        form = New.form()
        post = model.get_post(int(id))
        if not form.validates():
            return render.edit(post, form)
        model.update_post(int(id), form.d.title, form.d.subtitle, form.d.content)
        raise web.seeother('/')


class Login:

    form = web.form.Form(web.form.Textbox('name', web.form.notnull,
                         size=30, description='User Name:'),
                         web.form.Password('password',
                         size=30, description='Password:'),
                         web.form.Button('Login'),
                         web.form.Hidden('redir'),
                         )

    def GET(self):
        params = web.input()
        redir = params.get('redir')
        form = self.form()
        form.redir.set_value(redir)
        return render.login(form)

    def POST(self):
        form = self.form()
        params = web.input()
        username = params.name
        password = params.password
        if not form.validates():
            return render.login(form, 'invalid input')
        user = model.login(username, password)
        if not user:
            return render.login(form, 'bad username or password')

        redir = form.d.redir or '/'
        session.user = user
        raise web.seeother(redir)


class Logout:
    def GET(self):
        session.user = None
        raise web.seeother('/')


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-f', '--flush', action='store_true', default=False)
    options, args = parser.parse_args()
    if options.flush:
        model.flushdb(DB_SETTINGS)
    else:
        model.initdb(DB_SETTINGS)
    app.run()
