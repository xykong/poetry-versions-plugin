import subprocess
import sys


def run_command(command, timeout=60):
    """Execute a system command and return its output."""
    print(f"Executing command: {command}")

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        stdout, stderr = process.communicate(timeout=timeout)
        print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        print(f"Command timed out after {timeout} seconds")
        raise

    # Check return code
    if process.returncode != 0:
        print(f"Command failed with return code {process.returncode}")
        print(f"Error output: {stderr}")
        raise subprocess.CalledProcessError(process.returncode, command)

    return stdout


def highlight_text(text):
    # ANSI escape code for bold/highlighted text
    return f"\033[1m{text}\033[0m"


def check_develop_branch():
    """检查是否在 develop 分支上"""
    current_commit = run_command("git rev-parse HEAD")
    branches = run_command(f"git branch --contains {current_commit}")

    if "develop" not in branches:
        print("Error: Current commit is not on the develop branch. Exiting.")
        sys.exit(1)

    print("On the develop branch.")


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


def git_flow_release(version, version_type):
    """使用 git flow 进行版本发布"""
    run_command(f"git flow release start {version}")
    run_command(f"poetry version {version_type} --dry-run")
    run_command(f'git flow release finish {version} -m "publish v{version}"')


def publish_package():
    """切换到 master 分支并发布包"""
    run_command("git checkout master")
    run_command("poetry publish --build --dry-run")


def steps(total_steps):
    current_step = 0

    def step():
        nonlocal current_step
        result = f"{current_step}/{total_steps}"
        current_step += 1
        return result

    return step


def main():
    """主函数，执行发布流程"""
    if len(sys.argv) > 2:
        print("Usage: python scripts/release.py [major|minor|patch]")
        sys.exit(1)

    step = steps(6)

    print(highlight_text(f"{step()} Starting the release process..."))
    version_type = sys.argv[1] if len(sys.argv) == 2 else 'minor'

    print(highlight_text(f"{step()} Checking if you are on the develop branch..."))
    check_develop_branch()

    print(highlight_text(f"{step()} Checking for uncommitted changes..."))
    check_uncommitted_changes()

    # 获取下一个版本号
    print(highlight_text(f"{step()} Getting the next version number for {version_type}..."))
    new_version = get_next_version(version_type)

    print(highlight_text(f"{step()} Starting the git flow release process for version {new_version}..."))
    git_flow_release(new_version, version_type)

    print(highlight_text(f"{step()} Publishing the package..."))
    publish_package()

    print(highlight_text(f"\n{step()} 🎉🎉🎉 Release successful! The new version has been published "
                         "and uploaded to the repository! 🎉🎉🎉"))
    print(highlight_text("Thank you for your dedication and hard work. Keep going! 🚀"))
    print()


if __name__ == "__main__":
    main()
