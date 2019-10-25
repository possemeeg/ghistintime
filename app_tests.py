from ghist import GHistInTime
from unittest import main, TestCase, mock

class GHistTest(TestCase):
    def setUp(self):
        with GHistInTime() as gh:
            gh.clear()

    def test_adds_line(self):
        with GHistInTime() as gh:
            gh.add('command 1')
            self.assertEqual(len(gh.all()), 1)
            gh.add('command 2')
            self.assertEqual(len(gh.all()), 2)

    def test_clears(self):
        with GHistInTime() as gh:
            gh.add('command 1')
            self.assertEqual(len(gh.all()), 1)
            gh.clear()
            self.assertEqual(len(gh.all()), 0)

    def test_no_dupe_line(self):
        with GHistInTime() as gh:
            gh.add('command 1')
            gh.add('command 1')
            gh.add('command 1')
            self.assertEqual(len(gh.all()), 1)

    def test_retrieves_in_revers_order(self):
        with GHistInTime() as gh:
            for i in range(0,5):
                gh.add('command {}'.format(i))
            allr = gh.all()
            for i in range(0,5):
                self.assertEqual(allr[i], 'command {}'.format(4-i))

            gh.add('command 3'.format(i))
            self.assertEqual(gh.all()[0], 'command 3')


if __name__ == '__main__':
    main()
