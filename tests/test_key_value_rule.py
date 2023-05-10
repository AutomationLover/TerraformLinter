import pytest
from simple_tf_linter import KeyValueCheckRule, load_key_regex_rule_to_linter, TerraformLinter


@pytest.mark.parametrize("key, regex, parsed_data, expected_result", [
    ("aws_account", r"\d{12}", {"aws_account": "123456789012"}, True),
    ("aws_account", r"\d{12}", {"aws_account": "invalid_account"}, False),
    ("aws_arn", r"arn:aws[a-zA-Z-]*:[^:]*:[^:]*:(\d{12}|aws|\*):.*",
     {"aws_arn": "arn:aws:s3:us-west-2:123456789012:bucket/my_corporate_bucket"}, True),
    ("aws_arn", r"arn:aws[a-zA-Z-]*:[^:]*:[^:]*:(\d{12}|aws|\*):.*", {"aws_arn": "invalid_arn"}, False),
])
def test_load_key_regex_rule_to_linter(key, regex, parsed_data, expected_result):
    linter = TerraformLinter()
    key_regex_pairs = [
        {
            "key": key,
            "regex": regex,
        },
    ]

    load_key_regex_rule_to_linter(key_regex_pairs, linter)

    assert len(linter.rules) == 1, f"Expected 1 rule to be registered, but got {len(linter.rules)}"
    rule = linter.rules[0]

    assert isinstance(rule, KeyValueCheckRule), f"Expected rule to be instance of KeyValueCheckRule"
    assert rule.key == key, f"Expected key to be '{key}', but got '{rule.key}'"

    ok, error_logs = rule.check(parsed_data, None, None, ignore_check_file_path=True)
    
    if expected_result:
        assert ok
    else:
        assert not ok


@pytest.mark.parametrize(
    "key, value, name, description, file_path, dict_path, match_is_good, parsed_data, expected_result", [
        ("key", lambda val: val == "value", "test_rule", "test_description", None, None, True, {"key": "value"}, True),
        ("key", lambda val: val == "value", "test_rule", "test_description", None, None, True, {"key": "wrong_value"},
         False),
    ])
def test_key_value_check_rule_class(key, value, name, description, file_path, dict_path, match_is_good, parsed_data,
                                    expected_result):
    rule = KeyValueCheckRule(key, value, name, description, file_path, dict_path, match_is_good)
    
    ok, error_logs = rule.check(parsed_data, None, None, ignore_check_file_path=True)
    
    if expected_result:
        assert ok, f"Expected check to pass, but got error logs: {error_logs}"
    else:
        assert not ok, f"Expected check to fail, but it passed"
        