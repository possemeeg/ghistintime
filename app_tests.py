from ghist import ghist_add, ghist_get, ghist_clear
from unittest import main, TestCase, mock

class GHistTest(TestCase):

    TESTDB = 'testghist.db'

    def setUp(self):
        ghist_clear(self.TESTDB)

    def test_adds_line(self):
        ghist_add(self.TESTDB, 'command 1')
        self.assertEqual(len(ghist_get(self.TESTDB)), 1)
        ghist_add(self.TESTDB, 'command 2')
        self.assertEqual(len(ghist_get(self.TESTDB)), 2)

    def test_clears(self):
        ghist_add(self.TESTDB, 'command 1')
        self.assertEqual(len(ghist_get(self.TESTDB)), 1)
        ghist_clear(self.TESTDB)
        self.assertEqual(len(ghist_get(self.TESTDB)), 0)

    def test_no_dupe_line(self):
        ghist_add(self.TESTDB, 'command 1')
        ghist_add(self.TESTDB, 'command 1')
        ghist_add(self.TESTDB, 'command 1')
        self.assertEqual(len(ghist_get(self.TESTDB)), 1)

    def test_retrieves_in_order(self):
        for i in range(0,5):
            ghist_add(self.TESTDB, 'command {}'.format(i))
        getr = ghist_get(self.TESTDB)
        for i in range(0,5):
            self.assertEqual(getr[i], 'command {}'.format(i))

        ghist_add(self.TESTDB, 'command 3'.format(i))
        self.assertEqual(ghist_get(self.TESTDB, 1)[0], 'command 3')


if __name__ == '__main__':
    main()
