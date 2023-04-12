import pytest
from ghistintime import ghist_add, ghist_get, ghist_assign, ghist_exec
from unittest import main, TestCase, mock
from os import path, remove

TESTDB = 'testghist.db'

@pytest.fixture
def uses_test_db():
    _rm_test_db()

    with mock.patch('ghistintime._get_config', return_value = {
        'DEFAULT': {
            'db': TESTDB
            }
        }):
        yield None

    _rm_test_db()

def _rm_test_db():
    if path.exists(TESTDB):
        remove(TESTDB)

def test_adds_line(uses_test_db):
    ghist_add('command 1')
    assert len(ghist_get()) == 1
    ghist_add('command 2')
    assert len(ghist_get()) == 2

def test_no_dupe_line(uses_test_db):
    ghist_add('command 1')
    ghist_add('command 1')
    ghist_add('command 1')
    assert len(ghist_get()) == 1

def test_retrieves_in_order(uses_test_db):
    for i in range(0,5):
        ghist_add(f'command {i}')
    getr = ghist_get()
    for i in range(0,5):
        assert getr[i] == f'[{i+1}] command {i}'.format(i)

    ghist_add('command 3'.format(i))
    assert ghist_get(1)[0] == '[6] command 3'

def test_assign_alias(uses_test_db):
    ghist_add('command 1')
    ghist_add('command 2')
    ghist_add('command 3')
    ghist_assign(2, 'c2')
    assert ghist_get()[1] == '[c2] command 2'

@mock.patch('ghistintime.system')
def test_execute_command(mock_system, uses_test_db):
    ghist_add('command 1')
    ghist_add('command 2')
    ghist_add('command 3')
    ghist_exec(2)

    mock_system.assert_called_with(f'bash -i -c "command 2"')

@mock.patch('ghistintime.system')
def test_execute_command_by_shortcut(mock_system, uses_test_db):
    ghist_add('command 1')
    ghist_add('command 2')
    ghist_add('command 3')
    ghist_assign(2, 'c2')
    ghist_exec('c2')

    mock_system.assert_called_with(f'bash -i -c "command 2"')

    ghist_add('command 4')
    ghist_exec('c2')

