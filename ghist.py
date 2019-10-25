import sqlite3
import os
import sys
import argparse

class GHistInTime(object):
    def __init__(self, dbname):
        self.file = dbname

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        c = self.conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS ghist(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL UNIQUE,
            inserted INTEGER NOT NULL
        )
        ''')
        self.conn.commit()
        return self;

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

    def add(self, line):
        c = self.conn.cursor()
        c.execute('''
        DELETE FROM ghist
        WHERE command = ?
        ''', (line,))
        c.execute('''
        INSERT INTO ghist(command, inserted)
        VALUES(?, strftime('%s','now'))
        ''', (line,))
        self.conn.commit()
        c.close()

    def get(self, num=None):
        c = self.conn.cursor()
        try:
            num=int(num)
        except (TypeError, ValueError):
            num=None
        cmd = 'select command from (SELECT command, id FROM ghist order by id desc LIMIT {}) order by id'.format(num) if num else 'SELECT command FROM ghist order by id asc'
        c.execute(cmd)
        ret = [r for (r,) in c.fetchall()]
        self.conn.commit()
        c.close()
        return ret

    def clear(self):
        c = self.conn.cursor()
        c.execute('''
        DELETE FROM ghist
        ''')
        self.conn.commit()
        c.close()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True, help='sqlite3 file')
    parser.add_argument('command', choices=['get', 'put'])
    parser.add_argument('text', nargs='*')

    args = parser.parse_intermixed_args()

    with GHistInTime(args.database) as gh:
        if args.command == 'put':
            gh.add(' '.join(args.text))
        else:
            if args.command == 'get':
                for c in gh.get(args.text[0] if len(args.text) else None):
                     print(c)
    
