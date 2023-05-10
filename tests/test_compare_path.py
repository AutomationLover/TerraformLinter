import pytest
from simple_tf_linter.compare_path import check_file_path

@pytest.mark.parametrize("target_path, file_path, expected_result", [
    ("/some/*/path", "/some/dir/path", True),
    ("/some/**/path", "/some/dir/path", True),
    ("/some/**/path", "/some/dir/subdir/path", True),
    ("/some/*/path", "/some/dir/subdir/path", False),
    ("/some/*/*/*", "/some/dir/subdir/path", True),
    ("/some/*/subdir/*", "/some/dir/subdir/path", True),
    ("/some/*/subdir/*", "/some/dir/another_subdir/path", False),
])
def test_check_file_path(target_path, file_path, expected_result):
    result = check_file_path(target_path, file_path)
    assert result == expected_result
    