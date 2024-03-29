import sqlite3
import os
import sys
import argparse
import subprocess

class GHistConnection(object):
    def __init__(self, dbname):
        self.file = dbname

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
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

def ghist_add(dbfile, line):
    line = line.strip()
    with GHistConnection(dbfile) as c:
        c.cursor.execute('''
        DELETE FROM ghist
        WHERE command = ?
        ''', (line,))
        c.cursor.execute('''
        INSERT INTO ghist(command, inserted)
        VALUES(?, strftime('%s','now'))
        ''', (line,))

def ghist_get(dbfile, num=None, fmt=None):
    with GHistConnection(dbfile) as c:
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
        c.cursor.execute(cmd)
        return [(fmt or '[{r}] {c}').format(c=c,r=r,t=t) for (c,r,t) in c.cursor.fetchall()]

def ghist_get_assigned(dbfile, fmt=None):
    with GHistConnection(dbfile) as c:
        cmd = 'SELECT command, shortcut as ref FROM ghist where shortcut is not null ORDER BY id ASC'
        c.cursor.execute(cmd)
        return [(fmt or '[{r}] {c}').format(c=c,r=r) for (c,r,) in c.cursor.fetchall()]

def ghist_get_by_ref(dbfile, ref):
    i, s = _id_or_shortcut(ref)
    with GHistConnection(dbfile) as c:
        if i:
            c.cursor.execute('SELECT command, id, shortcut FROM ghist WHERE id = ?', (i,))
        else:
            c.cursor.execute('SELECT command, id, shortcut FROM ghist WHERE shortcut = ?', (s,))
        row = c.cursor.fetchone()
        if (len(row)):
            return row

def ghist_assign(dbfile, cur, alias):
    i, s = _id_or_shortcut(cur)
    alias = alias[0:4]
    with GHistConnection(dbfile) as c:
        c.cursor.execute('''
        UPDATE ghist SET shortcut = null
        WHERE shortcut = ?
        ''', (alias,))
        if i:
            c.cursor.execute('''
            UPDATE ghist SET shortcut = ?
            WHERE id = ?
            ''', (alias, i))
        else:
            c.cursor.execute('''
            UPDATE ghist SET shortcut = ?
            WHERE shortcut = ?
            ''', (alias, s))

def ghist_exec(dbfile, ref):
    cmd, i, shortcut = ghist_get_by_ref(dbfile, ref)

    with GHistConnection(dbfile) as c:
        c.cursor.execute('''
        DELETE FROM ghist
        WHERE id = ?
        ''', (i,))
        c.cursor.execute('''
        INSERT INTO ghist(command, shortcut, inserted)
        VALUES(?, ?, strftime('%s','now'))
        ''', (cmd,shortcut))

    cmd = cmd.replace('"', '""')
    #subprocess.run(['bash', '-i', '-c',] + cmd.split())
    #breakpoint()
    os.system(f'bash -i -c "{cmd}"')

def ghist_clear(dbfile):
    if os.path.exists(dbfile):
        os.remove(dbfile)
        
def _id_or_shortcut(ref):
    try:
        return int(ref), None
    except (TypeError, ValueError):
        return None, ref

def run(args):        

    if args.command == 'put':
        ghist_add(args.database, ' '.join(args.text))
        return
    
    if args.command == 'get':
        for c in ghist_get(args.database, args.text[0] if len(args.text) else None, args.text[1] if len(args.text) > 1 else None):
            print(c)
        return
    
    if args.command == 'ass':
        if len(args.text) < 2:
            for c in ghist_get_assigned(args.database):
                print(c)
        else:
            ghist_assign(args.database, args.text[0], args.text[1])

    if args.command == 'ex':
        if len(args.text) < 1:
            return
        ghist_exec(args.database, args.text[0])

    if args.command == 'ref':
        if len(args.text) < 1:
            return
        print(ghist_get_by_ref(args.database, args.text[0])[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True, help='sqlite3 file')
    parser.add_argument('command', choices=['get', 'put', 'ass', 'ex', 'ref'])
    parser.add_argument('text', nargs='*')

    run(parser.parse_intermixed_args())

