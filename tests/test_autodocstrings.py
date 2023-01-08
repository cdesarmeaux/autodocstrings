import openai
import pytest
import os
import tempfile
import sys
import autodocstrings
import autodocstrings.main

from openai.error import RateLimitError
from autodocstrings.main import (
    generate_docstring,
    update_docstrings_in_directory,
    update_docstrings_in_file,
    update_docstrings,
    _extract_exclude_list,
)


def test_generate_docstring(mocker):
    # Mock the openai.Completion.create method
    mock_completions = mocker.MagicMock()
    mock_completions.choices = [mocker.MagicMock()]
    mock_completions.choices[0].text = "Test docstring"
    mocker.patch.object(openai.Completion, "create", return_value=mock_completions)

    # Test the generate_docstring function
    code_block = "def foo():\n    pass"
    block_name = "foo"
    docstring = generate_docstring(code_block, block_name)
    assert docstring == "Test docstring"


def test_generate_docstring_retries_exceeded(mocker):
    # Set up the mock for the openai.Completion.create function
    mocker.patch.object(openai.Completion, "create", side_effect=RateLimitError)

    # Set up the mock for the time.sleep function
    mocker.patch("time.sleep", lambda x: None)

    # Call the generate_docstring function and capture the exit code
    with pytest.raises(SystemExit) as exit_code:
        generate_docstring("code_block", "block_name")

    # Assert that the exit code is 1
    assert exit_code.value.code == 1


def create_test_file_with_docstring(docstring: str) -> tempfile.NamedTemporaryFile:
    file_contents = f"""
def foo():
    {docstring}
    pass
"""
    test_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    test_file.write(file_contents)
    test_file.close()
    return test_file


def create_test_file_with_constructor() -> tempfile.NamedTemporaryFile:
    file_contents = f"""
def __init__():
    pass
"""
    test_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    test_file.write(file_contents)
    test_file.close()
    return test_file


def test_update_docstrings_in_file_replaces_existing_docstrings(mocker):
    # Create a test file with an existing docstring
    test_file = create_test_file_with_docstring('"""This is a docstring."""')

    mocker.patch.object(
        autodocstrings.main, "generate_docstring", return_value="Updated docstring"
    )

    # Replace the existing docstring
    update_docstrings_in_file(
        test_file.name,
        replace_existing_docstrings=True,
        skip_constructor_docstrings=False,
    )

    # Check that the docstring was replaced
    with open(test_file.name, "r") as f:
        updated_file_contents = f.read()
    assert "This is a docstring" not in updated_file_contents
    assert "Updated docstring" in updated_file_contents

    # Clean up the test file
    os.unlink(test_file.name)


def test_update_docstrings_in_file_does_not_replace_existing_docstrings(mocker):
    # Create a test file with an existing docstring
    test_file = create_test_file_with_docstring('"""This is a docstring."""')

    mocker.patch.object(
        autodocstrings.main, "generate_docstring", return_value="Updated docstring"
    )

    # Replace the existing docstring
    update_docstrings_in_file(
        test_file.name,
        replace_existing_docstrings=False,
        skip_constructor_docstrings=False,
    )

    # Check that the docstring was replaced
    with open(test_file.name, "r") as f:
        updated_file_contents = f.read()
    assert "This is a docstring" in updated_file_contents
    assert "Updated docstring" not in updated_file_contents

    # Clean up the test file
    os.unlink(test_file.name)


def test_update_docstrings_in_file_skips_constructor_docstrings(mocker):
    # Create a test file with an existing docstring
    test_file = create_test_file_with_constructor()

    mocker.patch.object(
        autodocstrings.main, "generate_docstring", return_value="Updated docstring"
    )

    # Replace the existing docstring
    update_docstrings_in_file(
        test_file.name,
        replace_existing_docstrings=False,
        skip_constructor_docstrings=True,
    )

    # Check that the docstring was replaced
    with open(test_file.name, "r") as f:
        updated_file_contents = f.read()
    assert "Updated docstring" not in updated_file_contents

    # Clean up the test file
    os.unlink(test_file.name)


def test_update_docstrings_in_file_does_not_skip_constructor_docstrings(mocker):
    # Create a test file with an existing docstring
    test_file = create_test_file_with_constructor()

    mocker.patch.object(
        autodocstrings.main, "generate_docstring", return_value="Updated docstring"
    )

    # Replace the existing docstring
    update_docstrings_in_file(
        test_file.name,
        replace_existing_docstrings=False,
        skip_constructor_docstrings=False,
    )

    # Check that the docstring was replaced
    with open(test_file.name, "r") as f:
        updated_file_contents = f.read()
    assert "Updated docstring" in updated_file_contents

    # Clean up the test file
    os.unlink(test_file.name)


def test_update_docstrings_in_directory(mocker):
    # Create a test directory structure with Python files
    test_dir = tempfile.TemporaryDirectory()
    subdir_1 = os.path.join(test_dir.name, "subdir_1")
    os.makedirs(subdir_1)
    file_1 = os.path.join(test_dir.name, "file_1.py")
    file_2 = os.path.join(subdir_1, "file_2.py")
    open(file_1, "w").close()
    open(file_2, "w").close()
    # Mock the update_docstrings_in_file function
    mocker.patch.object(
        autodocstrings.main, "update_docstrings_in_file", return_value=None
    )

    # Call the update_docstrings_in_directory function
    update_docstrings_in_directory(test_dir.name, True, False, [], [])

    # Check that update_docstrings_in_file was called for all Python files in the directory and its subdirectories
    autodocstrings.main.update_docstrings_in_file.assert_any_call(file_1, True, False)
    autodocstrings.main.update_docstrings_in_file.assert_any_call(file_2, True, False)

    # Clean up the test directory
    test_dir.cleanup()


def test_update_docstrings_in_directory_with_exclude_files(mocker):
    # Create a test directory structure with Python files
    test_dir = tempfile.TemporaryDirectory()
    file_1 = os.path.join(test_dir.name, "file_1.py")
    open(file_1, "w").close()
    # Mock the update_docstrings_in_file function
    mocker.patch.object(
        autodocstrings.main, "update_docstrings_in_file", return_value=None
    )

    # Call the update_docstrings_in_directory function
    update_docstrings_in_directory(test_dir.name, True, False, [], ["file_1.py"])

    # Check that update_docstrings_in_file was not called for all Python files in the directory and its subdirectories
    autodocstrings.main.update_docstrings_in_file.assert_not_called()

    # Clean up the test directory
    test_dir.cleanup()


def test_update_docstrings_in_directory_with_exclude_dirs(mocker):
    # Create a test directory structure with Python files
    test_dir = tempfile.TemporaryDirectory()
    subdir_1 = os.path.join(test_dir.name, "subdir_1")
    os.makedirs(subdir_1)
    file_2 = os.path.join(subdir_1, "file_2.py")
    open(file_2, "w").close()
    # Mock the update_docstrings_in_file function
    mocker.patch.object(
        autodocstrings.main, "update_docstrings_in_file", return_value=None
    )

    # Call the update_docstrings_in_directory function
    update_docstrings_in_directory(test_dir.name, True, False, ["subdir_1"], [])

    # Check that update_docstrings_in_file was not called for all Python files in the directory and its subdirectories
    autodocstrings.main.update_docstrings_in_file.assert_not_called()

    # Clean up the test directory
    test_dir.cleanup()


def test_update_docstrings_input_is_valid_file(mocker):
    os.environ["OPENAI_API_KEY"] = "test_key"
    # Create a test file with an existing docstring
    open("test_file.py", "w").close()

    mocker.patch.object(
        autodocstrings.main, "update_docstrings_in_file", return_value=None
    )

    update_docstrings(
        "test_file.py",
        replace_existing_docstrings=True,
        skip_constructor_docstrings=False,
        exclude_directories=[],
        exclude_files=["test_file.py"],
    )
    autodocstrings.main.update_docstrings_in_file.assert_not_called()

    # Test updating docstrings in the file
    update_docstrings(
        "test_file.py",
        replace_existing_docstrings=True,
        skip_constructor_docstrings=False,
    )
    autodocstrings.main.update_docstrings_in_file.assert_called_once_with(
        "test_file.py", True, False
    )

    # Clean up the test file
    os.unlink("test_file.py")


def test_update_docstrings_input_is_valid_directory(mocker):
    os.environ["OPENAI_API_KEY"] = "test_key"
    # Create a test directory structure with Python files
    test_dir = tempfile.TemporaryDirectory()

    mocker.patch.object(
        autodocstrings.main, "update_docstrings_in_directory", return_value=None
    )

    update_docstrings(
        test_dir.name,
        replace_existing_docstrings=True,
        skip_constructor_docstrings=False,
        exclude_directories=[os.path.basename(test_dir.name)],
        exclude_files=[],
    )
    autodocstrings.main.update_docstrings_in_directory.assert_not_called()

    # Test updating docstrings in the file
    update_docstrings(
        test_dir.name,
        replace_existing_docstrings=True,
        skip_constructor_docstrings=False,
    )
    autodocstrings.main.update_docstrings_in_directory.assert_called_once_with(
        test_dir.name, True, False, [], []
    )

    # Clean up the dir
    test_dir.cleanup()


def test_update_docstrings_invalid_input(mocker):
    os.environ["OPENAI_API_KEY"] = "test_key"

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        update_docstrings("invalid_input", True, False)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_update_docstrings_invalid_api_key(mocker):
    os.environ.pop("OPENAI_API_KEY")
    open("test_file.py", "w").close()

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        update_docstrings("test_file.py", True, False)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_extract_exclude_list(mocker):
    # Test empty exclude string
    assert _extract_exclude_list("") == []

    # Test single item in exclude string
    assert _extract_exclude_list("test.py") == ["test.py"]

    # Test multiple items in exclude string
    assert _extract_exclude_list("test1.py,test2.py,test3.py") == [
        "test1.py",
        "test2.py",
        "test3.py",
    ]

    # Test multiple items with whitespace in exclude string
    assert _extract_exclude_list("  test1.py ,  test2.py ,  test3.py  ") == [
        "test1.py",
        "test2.py",
        "test3.py",
    ]


def test_main(mocker):
    # Mock the update_docstrings function
    mocker.patch.object(autodocstrings.main, "update_docstrings", return_value=None)

    # Set the command-line arguments
    sys.argv = [
        "autodocstrings",
        "input_path",
        "--replace-existing-docstrings",
        "--skip-constructor-docstrings",
        "--exclude-directories",
        "dir1,dir2",
        "--exclude-files",
        "file1,file2",
    ]

    # Call the main function
    autodocstrings.main.main()

    # Check that update_docstrings was called with the correct arguments
    autodocstrings.main.update_docstrings.assert_called_once_with(
        "input_path",
        True,
        True,
        ["dir1", "dir2"],
        ["file1", "file2"],
    )
