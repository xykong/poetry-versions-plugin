import os
from datetime import datetime

import git


def get_git_info():
    """
    获取当前Git仓库的相关信息，包括分支名称、最近提交的短SHA、提交数量、仓库是否有未提交的修改，以及当前时间。
    """
    repo = git.Repo(search_parent_directories=True)
    branch = repo.active_branch.name
    commit = repo.head.commit.hexsha[:7]
    commit_count = sum(1 for _ in repo.iter_commits(branch))
    is_dirty = repo.is_dirty()
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "branch": branch,
        "commit": commit,
        "commit_count": commit_count,
        "is_dirty": is_dirty,
        "datetime": current_datetime
    }


def update_readme(readme_path, info):
    """
    更新README.md文件中的占位符，替换成Git信息。

    :param readme_path: README.md文件的路径
    :param info: 包含Git信息的字典
    """
    with open(readme_path, 'r+') as f:
        content = f.read()
        # 使用占位符替换内容
        content = content.replace("<!-- BRANCH -->", info['branch'])
        content = content.replace("<!-- COMMIT -->", info['commit'])
        content = content.replace("<!-- COMMIT_COUNT -->", str(info['commit_count']))
        content = content.replace("<!-- IS_DIRTY -->", str(info['is_dirty']))
        content = content.replace("<!-- DATETIME -->", info['datetime'])

        f.seek(0)
        f.write(content)
        f.truncate()


def update_py_file(py_path, info):
    """
    创建或更新Python文件，将Git信息写入其中。

    :param py_path: Python文件的路径
    :param info: 包含Git信息的字典
    """
    # 获取目录路径
    dir_path = os.path.dirname(py_path)

    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    with open(py_path, 'w') as f:
        f.write("# Auto-generated version info\n\n")

        for key, value in info.items():
            # 根据值的类型格式化输出
            if isinstance(value, str):
                f.write(f"{key} = '{value}'\n")
            else:
                f.write(f"{key} = {value}\n")


def update_pyproject(info, pyproject, io):
    """
    更新pyproject.toml文件，将Git信息和版本号写入其中。
    :param info: 包含Git信息的字典
    :param pyproject: command.poetry.pyproject command 对象
    :param io:
    :return: None
    """

    # 更新 pyproject.toml
    try:
        # 获取版本号
        # version = command.poetry.package.version.text
        version = str(pyproject.data["tool"]["poetry"]["version"])

        if 'versions' not in pyproject.data['tool']:
            pyproject.data['tool']['versions'] = {}

        versions = pyproject.data['tool']['versions']

        # Loop through the info dictionary and update each field
        for key, value in info.items():
            versions[key] = value

        # Update the version separately
        versions['version'] = version

    except KeyError as ex:
        io.write_line(f'Error with parsing pyproject: {ex}')
        return

    # 保存更新
    pyproject.save()