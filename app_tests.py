from ghist import ghist_add, ghist_get, ghist_clear, ghist_assign, ghist_exec
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
            ghist_add(self.TESTDB, f'command {i}')
        getr = ghist_get(self.TESTDB)
        for i in range(0,5):
            self.assertEqual(getr[i], f'[{i+1}] command {i}'.format(i))

        ghist_add(self.TESTDB, 'command 3'.format(i))
        self.assertEqual(ghist_get(self.TESTDB, 1)[0], '[6] command 3')

    def test_assign_alias(self):
        ghist_add(self.TESTDB, 'command 1')
        ghist_add(self.TESTDB, 'command 2')
        ghist_add(self.TESTDB, 'command 3')
        ghist_assign(self.TESTDB, 2, 'c2')
        self.assertEqual(ghist_get(self.TESTDB)[1], '[c2] command 2')

    @mock.patch('subprocess.run')
    def test_execute_command(self, sc):
        ghist_add(self.TESTDB, 'command 1')
        ghist_add(self.TESTDB, 'command 2')
        ghist_add(self.TESTDB, 'command 3')
        ghist_exec(self.TESTDB, 2)
        sc.assert_called_with(['command', '2'], shell=True)

    @mock.patch('subprocess.run')
    def test_execute_command_by_shortcut(self, sc):
        ghist_add(self.TESTDB, 'command 1')
        ghist_add(self.TESTDB, 'command 2')
        ghist_add(self.TESTDB, 'command 3')
        ghist_assign(self.TESTDB, 2, 'c2')
        ghist_exec(self.TESTDB, 'c2')
        sc.assert_called_with(['command', '2'], shell=True)
        ghist_add(self.TESTDB, 'command 4')
        ghist_exec(self.TESTDB, 'c2')

if __name__ == '__main__':
    main()
