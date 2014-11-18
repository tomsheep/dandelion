# -*- coding: utf-8 -*-
import web
import datetime
import md5


db = None


def encrypt_passowrd(password):
    return md5.new(password).hexdigest()


def connectdb(settings):
    dbn = settings['dbn']
    config = settings['config']
    return web.database(dbn=dbn, **config)


def initdb(settings):
    global db
    db = connectdb(settings)
    return db


def flushdb(settings):
    _db = initdb(settings)
    schema_file = settings['schema']
    dbn = settings['dbn']
    sql = open(schema_file).read()
    print sql
    if dbn == 'sqlite':
        _db.ctx.db.executescript(sql)
    elif dbn == 'mysql':
        connection = _db.ctx.db
        cursor = connection.cursor()
        cursor.execute(sql)
        while cursor.nextset():
            pass
    else:
        raise
    new_user('xiaopu', '123')


def get_posts():
    return db.select('entries', order='id DESC')


def get_post(id):
    try:
        return db.select('entries', where='id=$id', vars=locals())[0]
    except IndexError:
        return None


def new_post(title, subtitle, text):
    db.insert('entries', title=title, subtitle=subtitle, content=text,
              posted_on=datetime.datetime.utcnow())


def del_post(id):
    db.delete('entries', where='id=$id', vars=locals())


def update_post(id, title, subtitle, text):
    db.update('entries', where='id=$id', vars=locals(), title=title,
              subtitle=subtitle, content=text)


def get_user(id):
    try:
        return db.select('users', where='id=$id', vars=locals())[0]
    except IndexError:
        return None


def get_user_by_name(name):
    try:
        return db.select('users', where='name=$name', vars=locals())[0]
    except IndexError:
        return None


def login(name, password):
    user = get_user_by_name(name)
    if user and encrypt_passowrd(password) == user['password']:
        return {'id': user['id'], 'name': user['name']}


def new_user(name, password):
    password = encrypt_passowrd(password)
    db.insert('users', name=name, password=password,
              create_time=datetime.datetime.utcnow())


def del_user(id):
    db.delete('users', where='id=$id', vars=locals())


def update_user(id, name, password):
    password = encrypt_passowrd(password)
    db.update('users', where='id=$id', vars=locals(), name=name, password=password)
