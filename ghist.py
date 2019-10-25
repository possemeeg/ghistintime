import sqlite3
import os


class GHistInTime(object):
    def __init__(self):
        self.file = 'ghist.db'

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

    def all(self):
        c = self.conn.cursor()
        c.execute('''
        SELECT command FROM ghist order by id desc
        ''')
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
        
        
    
