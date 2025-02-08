import subprocess

import pexpect
import pytest
from scripts.release import run_command


def test_run_command_basic():
    # Test a simple command, such as "echo"
    command = "echo 'Hello, World!'"
    output = run_command(command)
    assert "Hello, World!" in output


def test_run_command_long_output(capsys):
    # Test a command with long output
    command = "yes | head -n 10"
    with capsys.disabled():
        output = run_command(command)
    assert len(output.split('\n')) == 11  # 10 lines of "y" plus one additional empty line


def test_run_command_nonexistent_command():
    # Test a nonexistent command
    command = "nonexistent_command"

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        run_command(command)

    # Access the exception information
    exception = excinfo.value
    assert exception.cmd == command  # Verify the command
    assert exception.stdout is not None  # Check if stderr is captured

    # Print or inspect the command and stderr
    print(f"Command: {exception.cmd}")
    print(f"Stderr: {exception.stderr}")


def test_run_command_interactive():
    # Test an interactive command
    command = "python3 -c \"print('Enter something:'); input()\""
    # Use pexpect's spawn to simulate interaction
    child = pexpect.spawn(command, encoding='utf-8')
    child.expect("Enter something:")
    child.sendline("test input")
    child.expect(pexpect.EOF)
    output = child.before
    assert "test input" in output


def test_run_command_with_input():
    # Test a command that requires to be input
    command = "python3 -c \"print('Enter something:'); user_input = input(); print(user_input)\""
    output = run_command(command, user_input="test input\n")
    assert "test input" in output


def test_run_command_error_output():
    # Test a command with error output
    command = "ls non_existent_directory"

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        output = run_command(command)
        print('output:', output)

    # Access the exception information
    exception = excinfo.value
    assert exception.cmd == command  # Verify the command
    assert exception.stdout is not None  # Check if stderr is captured

    assert "No such file or directory" in exception.stdout


def test_run_command_no_output():
    # Test a command with no output
    command = "true"
    output = run_command(command)
    assert output == ""


def test_run_command_large_data():
    # Test handling a large amount of data
    large_data = 'A' * 100000  # 100kB of data
    command = f"echo {large_data}"
    output = run_command(command)
    assert large_data in output


def test_run_command_timeout():
    # Test command timeout
    command = "sleep 2"
    try:
        output = run_command(command)
        print('output:', output)
    except pexpect.exceptions.TIMEOUT:
        pytest.fail("Command timed out unexpectedly")


# pytest fixture to run before each test
@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Prepare any pre-test setup here
    yield
    # Teardown: Clean up any post-test data here


def test_run_command_with_env():
    # Test command with environment variables
    command = "echo $TEST_ENV_VAR"
    output = run_command(command, env={'TEST_ENV_VAR': 'Hello'})
    assert "Hello" in output


def test_run_command_with_pipe():
    # Test command with pipe
    command = "echo 'Hello, World!' | grep 'Hello'"
    output = run_command(command)
    assert "Hello, World!" in output


def test_run_command_background():
    # Test command running in the background
    command = "sleep 1 &"
    output = run_command(command)
    assert output == ""  # Command should not produce output


# def test_run_command_permission_denied():
#     # Test command with permission denied
#     command = "cat /root/secret_file"
#     output = run_command(command)
#     assert "Permission denied" in output


# def test_run_command_timeout_handling():
#     # Test timeout handling
#     command = "sleep 5"
#     with pytest.raises(pexpect.exceptions.TIMEOUT):
#         run_command(command, timeout=1)


def test_run_command_concurrent_execution():
    # Test concurrent execution of commands
    command1 = "echo 'First'"
    command2 = "echo 'Second'"
    output1 = run_command(command1)
    output2 = run_command(command2)
    assert "First" in output1
    assert "Second" in output2
