
<p align="center">
  <img src="https://storage.googleapis.com/cdesarmeaux_autodocstrings/autotocstrings_logo.png" alt="Logo" align="center">
  <h1 align="center"> autodocstrings </h1>
</p>




**Source Code**: <a href="https://github.com/cdesarmeaux/autodocstrings" target="_blank">https://github.com/cdesarmeaux/autodocstrings</a>

<p align="center">
<a href="https://github.com/cdesarmeaux/autodocstrings/actions/workflows/run_tests_and_report.yml" target="_blank">
    <img src="https://github.com/cdesarmeaux/autodocstrings/actions/workflows/run_tests_and_report.yml/badge.svg" alt="Test">
</a>
<a href="https://github.com/cdesarmeaux/autodocstrings/actions/workflows/tag_and_release_package.yml" target="_blank">
    <img src="https://github.com/cdesarmeaux/autodocstrings/actions/workflows/tag_and_release_package.yml/badge.svg" alt="Test">
</a>
</p>


---

<p align="center">
<img src="https://storage.googleapis.com/cdesarmeaux_autodocstrings/demo.gif" alt="Demo">
</p>

Autodocstrings is a command-line tool with the following key features:

* Updates the docstrings in Python files using the OpenAI API.
* Can process a single file or a directory of files, including all subdirectories.

Autodocstrings uses the OpenAI api to generate docstrings, so these are not guaranteed to be perfect. However, they are a good starting point for writing your own docstrings.

The code-davinci-002 model is used to generate the docstrings. This model is trained on a large corpus of Python code, including docstrings. The model is able to generate docstrings that are similar to those found in the corpus.

Autodocstrings will work best for code that already has good type hints. Without type hints, the OpenAI API will have to guess input and return types, which may not be accurate.

---

## Requirements

* Python 3.6+
* A valid openai api key. You can get one [here](https://beta.openai.com/docs/api-reference/authentication). This is currently free.

---

## Installation
To install the dependencies for this tool, run the following command:

<div class="termy">

```console
$ pip install autodocstrings
```

</div>

---
## Usage
To use this tool, run the following commands:

<div class="termy">

```console
$ export OPENAI_API_KEY=1234567890
$ autodocstrings INPUT `       
    [--replace-existing-docstrings] `
    [--skip-constructor-docstrings] `
    [--exclude-directories EXCLUDE_DIRECTORIES] `
    [--exclude-files EXCLUDE_FILES]
```

</div>

Where INPUT is a Python file or directory containing Python files to update the docstrings in, API_KEY is your OpenAI API key, and the optional flags --replace-existing-docstrings and --skip-constructor-docstrings can be used to skip updating docstrings for constructors (__init__ methods) and replacing existing docstirngs. EXCLUDE_DIRECTORIES and EXCLUDE_FILES are comma-separated lists of directories and files to exclude from the update.

---
## Examples
Update the docstrings in all Python files in the my_code directory:

<div class="termy">

```console
$ autodocstrings my_code/
```

</div>

Update the docstrings in the my_file.py file:

<div class="termy">

```console
$ autodocstrings my_file.py
```

</div>

Update the docstrings in all Python files in the my_code directory and replace existing ones:

<div class="termy">

```console
$ autodocstrings my_code/ --replace-existing-docstrings
```

</div>

Update the docstrings in all Python files in the my_code directory, but skip updating docstrings for class constructors (__init__ methods):

<div class="termy">

```console
$ autodocstrings my_code/ --skip-constructor-docstrings
```

</div>

Update the docstrings in all Python files in the my_code directory, but exlcude the exclude_dir directory and the exclude_file_1.py and exclude_file_2.py files:

<div class="termy">

```console
$ autodocstrings my_code/ --exclude-directories exclude_dir --exclude-files exclude_file_1.py,exclude_file_2.py
```

</div>

---
## License
This project is licensed under the MIT License. See the LICENSE file for details.

---
## Limitations

* The python functions are being passed to the OpenAI API as independent code blocks. This means that the docstrings are not aware of the context of the function. If functions are written independently of each other, then this should not be a problem.
* The format of the docstring is not always consistent, so you may need to manually fix some of the docstrings. You shouldn't use this in a ci/cd pipeline.
* Input length is limited to the maximum input length of the OpenAI API. This is currently 2048 characters. If your function is larger than this then the docstring will not be updated.
* OpenAI API can be slow.

---
