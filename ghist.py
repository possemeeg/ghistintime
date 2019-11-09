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

def ghist_get(dbfile, num=None, fmt='[{r}] {c}'):
    with GHistConnection(dbfile) as c:
        try:
            num=int(num)
        except (TypeError, ValueError):
            num=None
        cmd = f'''SELECT command, ref FROM
           (SELECT command, id, coalesce(shortcut, id) as ref
               FROM ghist ORDER BY id DESC LIMIT {num}) ORDER BY id
           ''' if num else 'SELECT command, coalesce(shortcut, id) as ref FROM ghist ORDER BY id ASC'
        c.cursor.execute(cmd)
        return [fmt.format(c=c,r=r) for (c,r,) in c.cursor.fetchall()]

def ghist_get_by_ref(dbfile, ref):
    i, s = _id_or_shortcut(ref)
    with GHistConnection(dbfile) as c:
        if i:
            c.cursor.execute('SELECT command FROM ghist WHERE id = ?', (i,))
        else:
            c.cursor.execute('SELECT command FROM ghist WHERE shortcut = ?', (s,))
        row = c.cursor.fetchone()
        if (len(row)):
            return row[0]

def ghist_assign(dbfile, cur, alias):
    i, s = _id_or_shortcut(cur)
    with GHistConnection(dbfile) as c:
        if i:
            c.cursor.execute('''
            UPDATE ghist SET shortcut = ?
            WHERE id = ?
            ''', (alias[0:4], i))
        else:
            c.cursor.execute('''
            UPDATE ghist SET shortcut = ?
            WHERE shortcut = ?
            ''', (alias[0:4], s))

def ghist_exec(dbfile, ref):
    cmd = ghist_get_by_ref(dbfile, ref)
    subprocess.call(cmd.split())

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
        for c in ghist_get(args.database, args.text[0] if len(args.text) else None):
            print(c)
        return
    
    if args.command == 'ass':
        if len(args.text) < 2:
            return
        ghist_assign(args.database, args.text[0], args.text[1])

    if args.command == 'ex':
        if len(args.text) < 1:
            return
        ghist_exec(args.database, args.text[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True, help='sqlite3 file')
    parser.add_argument('command', choices=['get', 'put', 'ass', 'ex'])
    parser.add_argument('text', nargs='*')

    run(parser.parse_intermixed_args())

