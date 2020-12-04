from ldcoolp.git_info import get_active_branch_name, get_latest_commit


def test_get_active_branch_name():

    assert isinstance(get_active_branch_name(), str)


def test_get_latest_commit():
    git_commit, git_short_commit = get_latest_commit()

    assert isinstance(git_commit, str)
    assert isinstance(git_short_commit, str)

    if not git_short_commit:  # Empty string
        assert len(git_short_commit) == 0
    else:
        assert len(git_short_commit) == 7
