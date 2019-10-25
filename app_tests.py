from ghist import GHistInTime
from unittest import main, TestCase, mock

class GHistTest(TestCase):

    TESTDB = 'testghist.db'

    def setUp(self):
        with GHistInTime(self.TESTDB) as gh:
            gh.clear()

    def test_adds_line(self):
        with GHistInTime(self.TESTDB) as gh:
            gh.add('command 1')
            self.assertEqual(len(gh.get()), 1)
            gh.add('command 2')
            self.assertEqual(len(gh.get()), 2)

    def test_clears(self):
        with GHistInTime(self.TESTDB) as gh:
            gh.add('command 1')
            self.assertEqual(len(gh.get()), 1)
            gh.clear()
            self.assertEqual(len(gh.get()), 0)

    def test_no_dupe_line(self):
        with GHistInTime(self.TESTDB) as gh:
            gh.add('command 1')
            gh.add('command 1')
            gh.add('command 1')
            self.assertEqual(len(gh.get()), 1)

    def test_retrieves_in_order(self):
        with GHistInTime(self.TESTDB) as gh:
            for i in range(0,5):
                gh.add('command {}'.format(i))
            getr = gh.get()
            for i in range(0,5):
                self.assertEqual(getr[i], 'command {}'.format(i))

            gh.add('command 3'.format(i))
            self.assertEqual(gh.get(1)[0], 'command 3')


if __name__ == '__main__':
    main()
