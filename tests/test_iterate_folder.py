import os
from simple_tf_linter.linter_basic import iterate_folder


def test_iterate_folder(mocker):
    start_folder = "/mock/root/directory"
    sub_folder = os.path.join(start_folder, "sub_folder")
    expected_files = [
        (os.path.join(start_folder, "file1.txt"), "file1.txt", "file1.txt"),
        (os.path.join(sub_folder, "file2.txt"), "file2.txt", os.path.join("sub_folder", "file2.txt")),
    ]

    mocker.patch("os.walk", return_value=[
        (start_folder, ['sub_folder'], ["file1.txt"]),
        (sub_folder, [], ["file2.txt"]),
    ])

    mocker.patch("os.path.join", side_effect=os.path.join)
    mocker.patch("os.path.relpath", side_effect=os.path.relpath)

    results = list(iterate_folder(start_folder))

    assert results == expected_files
    