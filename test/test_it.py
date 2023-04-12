from ghistintime import ghist_add, ghist_get, ghist_clear, ghist_assign, ghist_exec
from unittest import main, TestCase, mock

TESTDB = 'testghist.db'

def test_adds_line():
    ghist_clear(TESTDB)

    ghist_add(TESTDB, 'command 1')
    assert len(ghist_get(TESTDB)) == 1
    ghist_add(TESTDB, 'command 2')
    assert len(ghist_get(TESTDB)) == 2

def test_clears():
    ghist_clear(TESTDB)

    ghist_add(TESTDB, 'command 1')
    assert len(ghist_get(TESTDB)) == 1
    ghist_clear(TESTDB)
    assert len(ghist_get(TESTDB)) == 0

def test_no_dupe_line():
    ghist_clear(TESTDB)

    ghist_add(TESTDB, 'command 1')
    ghist_add(TESTDB, 'command 1')
    ghist_add(TESTDB, 'command 1')
    assert len(ghist_get(TESTDB)) == 1

def test_retrieves_in_order():
    ghist_clear(TESTDB)

    for i in range(0,5):
        ghist_add(TESTDB, f'command {i}')
    getr = ghist_get(TESTDB)
    for i in range(0,5):
        assert getr[i] == f'[{i+1}] command {i}'.format(i)

    ghist_add(TESTDB, 'command 3'.format(i))
    assert ghist_get(TESTDB, 1)[0] == '[6] command 3'

def test_assign_alias():
    ghist_clear(TESTDB)

    ghist_add(TESTDB, 'command 1')
    ghist_add(TESTDB, 'command 2')
    ghist_add(TESTDB, 'command 3')
    ghist_assign(TESTDB, 2, 'c2')
    assert ghist_get(TESTDB)[1] == '[c2] command 2'

@mock.patch('ghistintime.system')
def test_execute_command(mock_system):
    ghist_clear(TESTDB)

    ghist_add(TESTDB, 'command 1')
    ghist_add(TESTDB, 'command 2')
    ghist_add(TESTDB, 'command 3')
    ghist_exec(TESTDB, 2)

    mock_system.assert_called_with(f'bash -i -c "command 2"')

@mock.patch('ghistintime.system')
def test_execute_command_by_shortcut(mock_system):
    ghist_clear(TESTDB)

    ghist_add(TESTDB, 'command 1')
    ghist_add(TESTDB, 'command 2')
    ghist_add(TESTDB, 'command 3')
    ghist_assign(TESTDB, 2, 'c2')
    ghist_exec(TESTDB, 'c2')

    mock_system.assert_called_with(f'bash -i -c "command 2"')

    ghist_add(TESTDB, 'command 4')
    ghist_exec(TESTDB, 'c2')

