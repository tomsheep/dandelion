# -*- coding: utf-8 -*-
import web
import datetime
import os
from config import SQLITE_DB, DB_CREATE_SQL


def initdb(db_file, force=False):
    _db = web.database(dbn='sqlite', db=db_file)
    if force or not os.path.exists(db_file):
        print 'init db...'
        _db.query(DB_CREATE_SQL)
    return _db


db = initdb(SQLITE_DB)


def get_posts():
    return db.select('entries', order='id DESC')


def get_post(id):
    try:
        return db.select('entries', where='id=$id', vars=locals())[0]
    except IndexError:
        return None


def new_post(title, text):
    db.insert('entries', title=title, content=text,
              posted_on=datetime.datetime.utcnow())


def del_post(id):
    db.delete('entries', where='id=$id', vars=locals())


def update_post(id, title, text):
    db.update('entries', where='id=$id', vars=locals(), title=title,
              content=text)


