import subprocess
import sys


def run_command(command, user_input=None, env=None):
    """
    execute a command in a subprocess, optionally providing input and environment variables.

    :param command: the command to run.
    :param user_input: optional input to send to the command's standard input.
    :param env: optional dictionary of environment variables to set for the command.
    :return: combined output of stdout and stderr.
    :raises: subprocess.CalledProcessError if the command returns a non-zero exit code.
    """
    process = subprocess.Popen(
        command, shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
        env=env,
    )

    print('run_command:', command)

    # Use communicate method to send input and get output
    stdout, stderr = process.communicate(input=user_input)

    print('stdout:', stdout)
    print('stderr:', stderr)

    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command, stderr)

    # Return combined output
    return stdout + stderr


def highlight_text(text):
    """
    Return the given text formatted with ANSI escape codes for bold/highlighted text.

    :param text: The text to format.
    :return: Formatted text.
    """
    return f"\033[1m{text}\033[0m"


def check_develop_branch():
    """Check if the current branch is 'develop'."""
    current_commit = run_command("git rev-parse HEAD")
    branches = run_command(f"git branch --contains {current_commit}")

    if "develop" not in branches:
        print("Error: Current commit is not on the develop branch. Exiting.")
        sys.exit(1)

    print("On the develop branch.")


def check_uncommitted_changes():
    """Check for uncommitted changes in the repository."""
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

    # Retrieve and display commit details
    commit_details = run_command("git show --stat HEAD")
    print("\nCommit details:")
    print(commit_details)

    # Ask user if they want to continue
    confirm = input("\nDo you want to continue with the next steps? (y/n): ").strip().lower()
    if confirm != 'yes' and confirm != 'y':
        print("Stopping the process as requested.")
        sys.exit(1)

    print("Continuing with the next steps...")


def get_next_version(version_type):
    """Get the next version number based on the specified version type."""
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
    """Perform a release using git flow."""
    run_command(f"git flow release start {version}")
    # run_command(f"poetry version {version_type} --dry-run")
    run_command(f"poetry version {version_type}")
    run_command(f'git flow release finish {version} -m "publish v{version}"')


def publish_package():
    """Switch to the "master" branch and publish the package."""
    run_command("git checkout master")
    # run_command("poetry publish --build --dry-run")
    run_command("poetry publish --build")


def steps(total_steps):
    """
    Create a step counter for a multistep process.

    :param total_steps: The total number of steps in the process.
    :return: A function that returns the current step progress as a string.
    """
    current_step = 0

    def step():
        nonlocal current_step
        result = f"{current_step}/{total_steps}"
        current_step += 1
        return result

    return step


def main():
    """Main function to execute the release process."""
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

    # Get the next version number
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
