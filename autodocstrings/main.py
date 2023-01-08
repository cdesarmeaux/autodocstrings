import argparse
import ast
import astor
import openai
import os
import sys
import typer
import time
import textwrap
import black

from openai.error import RateLimitError
from typing import List


def generate_docstring(code_block: str, block_name: str) -> str:
    """
    Generate a new docstring for the given code block using the OpenAI API.

    Parameters:
    - code_block (str): The code block to generate a docstring for.
    - block_name (str): The name of the code block.

    Returns:
    - str: The generated docstring.
    """
    # Remove leading indentation from the code block
    stripped_code_block = textwrap.dedent(code_block)

    # Use the OpenAI API to generate a new docstring for the code block
    model_engine = "code-davinci-002"

    prompt = f"""# Python3
{stripped_code_block}

# Write a google-style function docstring for the {block_name} python function
\"""
"""

    max_retries = 5  # Maximum number of retries
    retries = 0  # Number of retries so far

    while retries < max_retries:
        try:
            completions = openai.Completion.create(
                engine=model_engine,
                prompt=prompt,
                temperature=0,
                max_tokens=150,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop=["#", '"""'],
            )
            return completions.choices[0].text

        except RateLimitError:
            # Handle rate limiting error
            typer.secho(
                f"####### OpenAI rate limit reached, waiting for 1 minute #######",
                fg=typer.colors.YELLOW,
            )
            time.sleep(60)  # Wait 1 minute before trying again
            retries += 1  # Increment the number of retries

    if retries == max_retries:
        typer.secho(
            f"Maximum number of retries exceeded. Giving up.",
            fg=typer.colors.RED,
        )
        sys.exit(1)


def update_docstrings_in_file(
    file: str, replace_existing_docstrings: bool, skip_constructor_docstrings: bool
) -> None:
    """
    Update the docstrings in a Python file.

    Parameters:
    - file (str): The path to the Python file to update the docstrings in.
    - replace_existing_docstrings (bool): Whether to replace existing docstrings.
    - skip_constructor_docstrings (bool): Whether to skip updating docstrings for class constructors (__init__ methods).
    """

    # Read the file contents
    with open(file, "r") as f:
        file_contents = f.read()

    # Parse the file contents into an AST
    tree = ast.parse(file_contents)

    # Find all function definitions
    nodes = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    # Iterate through the top-level nodes in the AST
    for node in nodes:
        # Skip the constructor definition if necessary
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "__init__"
            and skip_constructor_docstrings
        ):
            continue
        # Check if the node has a docstring
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Str)
        ):
            if not replace_existing_docstrings:
                # The node has a docstring, and we don't want to replace it
                continue
            # The node has a docstring, so remove it
            node.body.pop(0)

        typer.secho(
            f"Updating docstrings for {node.name} in {file}", fg=typer.colors.YELLOW
        )

        # Generate and update the docstring
        code_block = astor.to_source(node).strip()
        block_name = node.name
        docstring = generate_docstring(code_block, block_name)

        # Insert the docstring into the code
        node.body.insert(0, ast.Expr(value=ast.Str(s=docstring + "\n")))

    # Write the updated AST back to the file
    with open(file, "w") as f:
        source = astor.to_source(tree)
        formatted_source = black.format_str(source, mode=black.FileMode())
        f.write(formatted_source)


def update_docstrings_in_directory(
    directory: str,
    replace_existing_docstrings: bool,
    skip_constructor_docstrings: bool,
    exclude_directories: List[str] = [],
    exclude_files: List[str] = [],
) -> None:
    """
    Update the docstrings in all Python files in a directory and its subdirectories.

    Parameters:
    - directory (str): The path to the directory to update the docstrings in.
    - replace_existing_docstrings (bool): Whether to replace existing docstrings.
    - skip_constructor_docstrings (bool): Whether to skip updating docstrings for class constructors (__init__ methods).
    - exclude_directories (List[str]): A list of directories to exclude from the update.
    - exclude_files (List[str]): A list of files to exclude from the update.
    """
    # Iterate through the files and subdirectories in the directory
    for path in os.listdir(directory):
        full_path = os.path.join(directory, path)
        if os.path.isfile(full_path) and full_path.endswith(".py"):
            if os.path.basename(path) in exclude_files:
                # Skip the file if it is in the exclude list
                continue
            # Update the docstrings in the Python file
            update_docstrings_in_file(
                full_path, replace_existing_docstrings, skip_constructor_docstrings
            )
        elif os.path.isdir(full_path):
            if os.path.basename(full_path) in exclude_directories:
                # Skip the directory if it is in the exclude list
                continue
            # Update the docstrings in all Python files in the subdirectory
            update_docstrings_in_directory(
                full_path,
                replace_existing_docstrings,
                skip_constructor_docstrings,
                exclude_directories,
                exclude_files,
            )


def update_docstrings(
    input: str,
    replace_existing_docstrings: bool,
    skip_constructor_docstrings: bool,
    exclude_directories: List[str] = [],
    exclude_files: List[str] = [],
) -> None:
    """
    Update the docstrings in Python files and directories.

    Parameters:
    - input (str): The path to a Python file or directory containing Python files to update the docstrings in.
    - replace_existing_docstrings (bool): Whether to replace existing docstrings.
    - skip_constructor_docstrings (bool): Whether to skip updating docstrings for class constructors (__init__ methods).
    - exclude_directories (List[str]): A list of directories to exclude from the update.
    - exclude_files (List[str]): A list of files to exclude from the update.
    """
    # Set the OpenAI API key
    try:
        openai.api_key = os.environ["OPENAI_API_KEY"]
    except:
        typer.secho("OPENAI_API_KEY environment variable not set!", fg=typer.colors.RED)
        sys.exit(1)

    # Check if the input is a file or a directory
    if os.path.isfile(input) and input.endswith(".py"):
        # Check if the directory is in the list of excluded files
        if os.path.basename(input) in exclude_files:
            return
        # Update the docstrings in the file
        update_docstrings_in_file(
            input, replace_existing_docstrings, skip_constructor_docstrings
        )
    elif os.path.isdir(input):
        # Check if the directory is in the list of excluded directories
        if os.path.basename(input) in exclude_directories:
            return
        # Update the docstrings in all Python files in the directory and its subdirectories
        update_docstrings_in_directory(
            input,
            replace_existing_docstrings,
            skip_constructor_docstrings,
            exclude_directories,
            exclude_files,
        )
    else:
        # The input is not a valid file or directory
        typer.secho(
            "Invalid input. The input must be either a valid python file or a valid directory",
            fg=typer.colors.RED,
        )
        sys.exit(1)


def _extract_exclude_list(exclude: str) -> List[str]:
    """
    Extract a list of files and directories to exclude from a comma-separated string.

    Parameters:
    - exclude (str): A comma-separated string of files and directories to exclude.

    Returns:
    - List[str]: A list of files and directories to exclude.
    """
    return [x.strip() for x in exclude.split(",") if x.strip() != ""]


def main() -> None:
    # Parse the command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        help="The path to a Python file or directory containing Python files to update the docstrings in.",
    )
    parser.add_argument(
        "--replace-existing-docstrings",
        action="store_true",
        help="Skip updating docstrings for classes.",
    )
    parser.add_argument(
        "--skip-constructor-docstrings",
        action="store_true",
        help="Skip updating docstrings for class constructors (__init__ methods).",
    )
    parser.add_argument(
        "--exclude-directories",
        default="",
        help="Comma-seperated list of directories to exclude.",
    )
    parser.add_argument(
        "--exclude-files",
        default="",
        help="Comma-seperated list of files to exclude.",
    )
    args = parser.parse_args()

    exclude_directories = _extract_exclude_list(args.exclude_directories)
    exclude_files = _extract_exclude_list(args.exclude_files)

    # Update the docstrings
    update_docstrings(
        args.input,
        args.replace_existing_docstrings,
        args.skip_constructor_docstrings,
        exclude_directories,
        exclude_files,
    )
