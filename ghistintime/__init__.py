import sqlite3
from os import system, remove, path, makedirs
import sys
import argparse
import subprocess
from configparser import ConfigParser
from pathlib import Path

CONFIG_FILE = f'{Path.home()}/.config/ghistintime/config.cfg'
DEFAULT_DB = f'{Path.home()}/.config/ghistintime/ghist.db'

def gh():
    text_args = _text_args()
    for c in ghist_get(text_args[0] if text_args else None, text_args[1] if text_args and len(text_args) > 1 else None):
       print(c)

def gh_put():
    ghist_add(' '.join(_text_args()))

def ghe():
    text_args = _text_args()
    if len(text_args) < 1:
        return
    ghist_exec(text_args[0])

def ghr():
    text_args = _text_args()
    if len(text_args) < 1:
        return
    if len(args.text) < 1:
        return
    print(ghist_get_by_ref(text_args)[0])

def gha():
    text_args = _text_args()
    if len(text_args) < 2:
        for c in ghist_get_assigned():
            print(c)
    else:
        ghist_assign(text_args[0], text_args[1])

class GHistConnection(object):
    def __enter__(self):
        self.conn = sqlite3.connect(_get_db_file())
        self.cur = self.conn.cursor()
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS ghist(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shortcut VARCHAR(4),
            command TEXT NOT NULL UNIQUE,
            inserted INTEGER NOT NULL
        )
        ''')
        return self;

    @property
    def cursor(self):
        return self.cur

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        self.cur = None
        self.conn = None

def ghist_add(line):
    line = line.strip()
    with GHistConnection() as connection:
        connection.cursor.execute('''
        DELETE FROM ghist
        WHERE command = ?
        ''', (line,))
        connection.cursor.execute('''
        INSERT INTO ghist(command, inserted)
        VALUES(?, strftime('%s','now'))
        ''', (line,))

def ghist_get(num=None, fmt=None):
    with GHistConnection() as connection:
        try:
            num=int(num)
        except (TypeError, ValueError):
            num=None
        if num:
            cmd = f'''SELECT command, ref, datetime(inserted, 'unixepoch', 'localtime')
               FROM
               (SELECT command, id, coalesce(shortcut, id) as ref, inserted
                   FROM ghist ORDER BY id DESC LIMIT {num}) ORDER BY id
               ''' 
        else:
            cmd ='''SELECT command, coalesce(shortcut, id) as ref, datetime(inserted, 'unixepoch', 'localtime')
            FROM ghist ORDER BY id ASC'''
        connection.cursor.execute(cmd)

        return [(fmt or '[{r}] {c}').format(c=c,r=r,t=t) for (c,r,t) in connection.cursor.fetchall()]

def ghist_get_assigned(fmt=None):
    with GHistConnection() as connection:
        cmd = 'SELECT command, shortcut as ref FROM ghist where shortcut is not null ORDER BY id ASC'
        connection.cursor.execute(cmd)
        return [(fmt or '[{r}] {c}').format(c=c,r=r) for (c,r,) in connection.cursor.fetchall()]

def ghist_get_by_ref(ref):
    i, s = _id_or_shortcut(ref)
    with GHistConnection() as connection:
        if i:
            connection.cursor.execute('SELECT command, id, shortcut FROM ghist WHERE id = ?', (i,))
        else:
            connection.cursor.execute('SELECT command, id, shortcut FROM ghist WHERE shortcut = ?', (s,))
        row = connection.cursor.fetchone()
        if (len(row)):
            return row

def ghist_assign(cur, alias):
    i, s = _id_or_shortcut(cur)
    alias = alias[0:4]
    with GHistConnection() as connection:
        connection.cursor.execute('''
        UPDATE ghist SET shortcut = null
        WHERE shortcut = ?
        ''', (alias,))
        if i:
            connection.cursor.execute('''
            UPDATE ghist SET shortcut = ?
            WHERE id = ?
            ''', (alias, i))
        else:
            connection.cursor.execute('''
            UPDATE ghist SET shortcut = ?
            WHERE shortcut = ?
            ''', (alias, s))

def ghist_exec(ref):
    cmd, i, shortcut = ghist_get_by_ref(ref)

    with GHistConnection() as connection:
        connection.cursor.execute('''
        DELETE FROM ghist
        WHERE id = ?
        ''', (i,))
        connection.cursor.execute('''
        INSERT INTO ghist(command, shortcut, inserted)
        VALUES(?, ?, strftime('%s','now'))
        ''', (cmd,shortcut))

    cmd = cmd.replace('"', '""')
    system(f'bash -i -c "{cmd}"')

def _id_or_shortcut(ref):
    try:
        return int(ref), None
    except (TypeError, ValueError):
        return None, ref


def _get_config():
    config = ConfigParser()
    if path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        return config

    config['DEFAULT'] = {
            'db': DEFAULT_DB
            }
    
    db_dir = path.dirname(DEFAULT_DB)
    if not path.exists(db_dir):
        makedirs(db_dir)

    return config

def _get_db_file():
    return path.expanduser(_get_config()['DEFAULT']['db'])

def _text_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('text', nargs='*')
    args = parser.parse_intermixed_args()
    return args.text

