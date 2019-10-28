import sqlite3
import os
import sys
import argparse

class GHistConnection(object):
    def __init__(self, dbname):
        self.file = dbname

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        self.cur = self.conn.cursor()
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS ghist(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

def ghist_get(dbfile, num=None):
    with GHistConnection(dbfile) as c:
        try:
            num=int(num)
        except (TypeError, ValueError):
            num=None
        cmd = f'''select command from
           (SELECT command, id FROM ghist order by id desc LIMIT {num}) order by id
           ''' if num else 'SELECT command FROM ghist order by id asc'
        c.cursor.execute(cmd)
        return [r for (r,) in c.cursor.fetchall()]

def ghist_clear(dbfile):
    if os.path.exists(dbfile):
        os.remove(dbfile)
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True, help='sqlite3 file')
    parser.add_argument('command', choices=['get', 'put'])
    parser.add_argument('text', nargs='*')

    args = parser.parse_intermixed_args()

    if args.command == 'put':
        ghist_add(args.database, ' '.join(args.text))
    else:
        if args.command == 'get':
            for c in ghist_get(args.database, args.text[0] if len(args.text) else None):
                 print(c)
    
