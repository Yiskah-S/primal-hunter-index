from tools.validate_all_metadata import validate_all


def test_validate_all_metadata_runs_clean():
	assert validate_all() == 0
