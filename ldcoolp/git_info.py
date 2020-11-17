from pathlib import Path
from os.path import dirname, basename, exists, join

# Get git root
git_root = dirname(__file__.replace(f'/{basename(__file__)}', ''))


def get_active_branch_name(input_path=git_root):
    if exists(join(input_path, ".git", "HEAD")):
        head_dir = Path(input_path) / ".git" / "HEAD"
        with head_dir.open("r") as f:
            content = f.read().splitlines()

        for line in content:
            if line[0:4] == "ref:":
                return line.partition("refs/heads/")[2]
            else:
                return f"HEAD detached : {content}"
    else:
        return '.git structure does not exist'


def get_latest_commit(input_path=git_root):

    if exists(join(input_path, ".git", "HEAD")):
        head_dir = Path(input_path) / ".git" / "HEAD"
        with head_dir.open("r") as f:
            content = f.read().splitlines()

        for line in content:
            if line[0:4] == "ref:":
                head_path = Path(join(input_path, f".git/{line.partition(' ')[2]}"))
                with head_path.open('r') as g:
                    commit = g.read().splitlines()
            else:
                commit = content[0]
        return commit[0], commit[0][:7]  # full and short hash
    else:
        return '.git structure does not exist', ''
