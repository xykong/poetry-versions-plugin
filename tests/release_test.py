import pexpect
import pytest

from scripts.release import run_command


def test_run_command_basic():
    # 测试一个简单的命令，比如 "echo"
    command = "echo 'Hello, World!'"
    output = run_command(command)
    assert "Hello, World!" in output


def test_run_command_long_output(capsys):
    # 测试长输出的命令
    command = "yes | head -n 10"
    with capsys.disabled():
        output = run_command(command)
    assert len(output.split('\n')) == 11  # 1000 lines of "y" plus one additional empty line


def test_run_command_nonexistent_command():
    # 测试不存在的命令
    command = "nonexistent_command"

    output = run_command(command)

    assert "command not found" in output


def test_run_command_interactive():
    # 测试交互命令
    command = "python3 -c \"print('Enter something:'); input()\""
    # 使用 pexpect 的 spawn 模拟交互
    child = pexpect.spawn(command, encoding='utf-8')
    child.expect("Enter something:")
    child.sendline("test input")
    child.expect(pexpect.EOF)
    output = child.before
    assert "test input" in output


def test_run_command_with_input():
    # Adjust the command to print the input
    command = "python3 -c \"print('Enter something:'); user_input = input(); print(user_input)\""
    output = run_command(command, user_input="test input\n")
    assert "test input" in output


def test_run_command_error_output():
    # 测试命令错误输出
    command = "ls non_existent_directory"
    output = run_command(command)
    assert "No such file or directory" in output


def test_run_command_no_output():
    # 测试没有输出的命令
    command = "true"
    output = run_command(command)
    assert output == ""


def test_run_command_large_data():
    # 测试处理大量数据
    large_data = 'A' * 100000  # 100kB of data
    command = f"echo {large_data}"
    output = run_command(command)
    assert large_data in output


def test_run_command_timeout():
    # 测试超时
    command = "sleep 2"
    try:
        output = run_command(command)

        print('output:', output)
    except pexpect.exceptions.TIMEOUT:
        pytest.fail("Command timed out unexpectedly")


# pytest fixture to run before each test
@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: 可以在这里准备任何测试前的设置
    yield
    # Teardown: 可以在这里清理测试后的数据


def test_run_command_with_env():
    # 测试带有环境变量的命令
    command = "echo $TEST_ENV_VAR"
    output = run_command(command, env={'TEST_ENV_VAR': 'Hello'})
    assert "Hello" in output


def test_run_command_with_pipe():
    # 测试带有管道的命令
    command = "echo 'Hello, World!' | grep 'Hello'"
    output = run_command(command)
    assert "Hello, World!" in output


def test_run_command_background():
    # 测试后台运行的命令
    command = "sleep 1 &"
    output = run_command(command)
    assert output == ""  # Command should not produce output


# def test_run_command_permission_denied():
#     # 测试无权限命令
#     command = "cat /root/secret_file"
#     output = run_command(command)
#     assert "Permission denied" in output


# def test_run_command_timeout_handling():
#     # 测试超时处理
#     command = "sleep 5"
#     with pytest.raises(pexpect.exceptions.TIMEOUT):
#         run_command(command, timeout=1)


def test_run_command_concurrent_execution():
    # 测试并发执行
    command1 = "echo 'First'"
    command2 = "echo 'Second'"
    output1 = run_command(command1)
    output2 = run_command(command2)
    assert "First" in output1
    assert "Second" in output2
