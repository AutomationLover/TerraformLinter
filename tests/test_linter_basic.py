import json
import os
import pytest
from unittest import mock
from simple_tf_linter import TerraformLinter, Rule

PREFIX = "simple_tf_linter."
class TestRule:
    def test_check_raises_not_implemented_error(self):
        rule = Rule("Test Rule", "This is a test rule")
        with pytest.raises(NotImplementedError, match="You need to implement the 'check' method for each rule."):
            rule.check(None, None, None)


class TestTerraformLinter:
    @pytest.fixture
    def linter(self):
        return TerraformLinter()
    
    @pytest.fixture
    def sample_rule(self):
        class SampleRule(Rule):
            def check(self, parsed_data, file_name, path, ignore_check_file_path=False):
                return True, []
        
        return SampleRule("Sample Rule", "This is a sample rule")
    
    def test_register_rule(self, linter, sample_rule):
        assert len(linter.rules) == 0
        linter.register_rule(sample_rule)
        assert len(linter.rules) == 1
    
    @mock.patch(PREFIX+"linter_basic.TerraformLinter.parse_file")
    def test_lint_file(self, parse_file_mock, linter, sample_rule):
        parse_file_mock.return_value = {"sample_key": "sample_value"}
        linter.register_rule(sample_rule)
        
        file_path = "test_file_path"
        file_name = "test_file_name"
        relative_path = "test_relative_path"
        
        ok, error_logs = linter.lint_file(file_path, file_name, relative_path)
        
        assert ok is True
        assert error_logs == []
        parse_file_mock.assert_called_once_with(file_path)
    
    @mock.patch(PREFIX+"linter_basic.TerraformLinter.parse_file")
    def test_lint_file_with_error(self, parse_file_mock, linter, sample_rule):
        parse_file_mock.return_value = {"sample_key": "sample_value"}
        
        error_logs_sample = ["error_log_1", "error_log_2"]
        
        class ErrorRule(Rule):
            def check(self, parsed_data, file_name, path, ignore_check_file_path=False):
                return False, error_logs_sample
        
        error_rule = ErrorRule("Error Rule", "This is an error rule")
        linter.register_rule(sample_rule)
        linter.register_rule(error_rule)
        
        file_path = "test_file_path"
        file_name = "test_file_name"
        relative_path = "test_relative_path"
        
        ok, error_logs = linter.lint_file(file_path, file_name, relative_path)
        
        assert ok is False
        assert error_logs == error_logs_sample
        parse_file_mock.assert_called_once_with(file_path)
    
    def test_lint_json(self, linter, sample_rule):
        linter.register_rule(sample_rule)
        
        json_file_path = "test_json_file_path"
        json_data = {"sample_key": "sample_value"}
        
        with open(json_file_path, "w") as f:
            json.dump(json_data, f)
        
        ok, error_logs = linter.lint_json(json_file_path)
        
        assert ok is True
        assert error_logs == []
        
        os.remove(json_file_path)
    
    @mock.patch(PREFIX+"linter_basic.iterate_folder")
    @mock.patch(PREFIX+"linter_basic.TerraformLinter.lint_file")
    def test_lint_directory(self, lint_file_mock, iterate_folder_mock, linter):
        iterate_folder_mock.return_value = [
            ("file_path_1", "file_name_1", "relative_path_1"),
            ("file_path_2", "file_name_2", "relative_path_2"),
        ]
        lint_file_mock.return_value = (True, [])
        
        folder_path = "test_folder_path"
        ok, error_logs = linter.lint_directory(folder_path)
        
        assert ok is True
        assert error_logs == []
        iterate_folder_mock.assert_called_once_with(folder_path)
        assert lint_file_mock.call_count == 2
    
    @mock.patch(PREFIX+"linter_basic.iterate_folder")
    @mock.patch(PREFIX+"linter_basic.TerraformLinter.lint_file")
    def test_lint_directory_with_error(self, lint_file_mock, iterate_folder_mock, linter):
        iterate_folder_mock.return_value = [
            ("file_path_1", "file_name_1", "relative_path_1"),
            ("file_path_2", "file_name_2", "relative_path_2"),
        ]
        lint_file_mock.side_effect = [
            (True, []),
            (False, ["error_log_1", "error_log_2"]),
        ]
        
        folder_path = "test_folder_path"
        ok, error_logs = linter.lint_directory(folder_path)
        
        assert ok is False
        assert error_logs == ["error_log_1", "error_log_2"]
        iterate_folder_mock.assert_called_once_with(folder_path)
        assert lint_file_mock.call_count == 2
