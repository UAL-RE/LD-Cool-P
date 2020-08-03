from pathlib import Path


def get_active_branch_name(input_path="."):

    head_dir = Path(input_path) / ".git" / "HEAD"
    with head_dir.open("r") as f:
        content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]
