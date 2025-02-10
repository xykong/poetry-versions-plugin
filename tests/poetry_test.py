from pathlib import Path

from poetry.factory import Factory


def create_poetry_instance(pyproject_path: Path):
    """
    使用 Poetry 的 Factory 方法来创建 Poetry 实例。
    """
    # 通过 Factory 从 pyproject.toml 创建一个 Poetry 实例
    return Factory().create_poetry(pyproject_path)


def test_pyproject_file_parent(tmpdir):
    # 在临时目录中创建一个 pyproject.toml 文件
    pyproject_content = """
[tool.poetry]
name = "test-package"
version = "0.1.0"
description = "A test package"
authors = ["Author <author@example.com>"]
"""

    pyproject_path = tmpdir.join("pyproject.toml")
    pyproject_path.write(pyproject_content)

    # 创建 Poetry 实例
    poetry = create_poetry_instance(pyproject_path)

    # 验证 pyproject.file.path.parent 属性是否正确
    assert poetry.pyproject.file.path.parent == Path(tmpdir)
