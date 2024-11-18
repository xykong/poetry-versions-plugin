import subprocess
import sys


def run_command(command):
    """运行命令并返回输出"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print(result.stderr)
        sys.exit(result.returncode)
    return result.stdout.strip()


def check_uncommitted_changes():
    """检查是否有未提交的更改"""
    status = run_command("git status --porcelain")
    if not status:
        print("No uncommitted changes found.")
        return

    print("Uncommitted changes detected:")
    print(status)
    choice = input("Do you want to commit these changes? (y/n): ").strip().lower()
    if choice != 'yes' and choice != 'y':
        print("No changes committed. Exiting.")
        sys.exit(1)

    message = input("Enter commit message: ")
    run_command("git add .")
    run_command(f'git commit -m "{message}"')

    # 获取并显示提交的详细信息
    commit_details = run_command("git show --stat HEAD")
    print("\nCommit details:")
    print(commit_details)

    # 询问用户是否继续
    confirm = input("\nDo you want to continue with the next steps? (y/n): ").strip().lower()
    if confirm != 'yes' or confirm != 'y':
        print("Stopping the process as requested.")
        return

    print("Continuing with the next steps...")


def get_next_version(version_type):
    """获取下一个版本号"""
    # Execute the command and capture the output
    output = run_command(f"poetry version {version_type} --dry-run")

    # Split the output into lines
    lines = output.splitlines()

    # Assume the first line contains the version bump information
    first_line = lines[0]

    # Split the first line by spaces and get the last element which is the new version
    next_version = first_line.split()[-1]

    print(f"Next version: {next_version}")
    return next_version


def git_flow_release(version):
    """使用 git flow 进行版本发布"""
    run_command(f"git flow release start {version}")
    run_command("poetry version minor")
    run_command(f'git flow release finish {version} -m "publish v{version}"')


def publish_package():
    """切换到 master 分支并发布包"""
    run_command("git checkout master")
    run_command("poetry publish --build --dry-run")


def main():
    """主函数，执行发布流程"""
    if len(sys.argv) > 2:
        print("Usage: python scripts/release.py [major|minor|patch]")
        sys.exit(1)

    version_type = sys.argv[1] if len(sys.argv) == 2 else 'minor'

    check_uncommitted_changes()

    # 获取下一个版本号
    new_version = get_next_version(version_type)

    git_flow_release(new_version)
    publish_package()

    print("\n🎉🎉🎉 Release successful! The new version has been published and uploaded to the repository! 🎉🎉🎉")
    print("Thank you for your dedication and hard work. Keep going! 🚀")


if __name__ == "__main__":
    main()
