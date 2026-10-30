# CONTRIBUTING

This guide describes how to setup your python environment, gives tips and advises to discover the codebase, and explains the process to get your changes merged

## Setting up your environment

### Clone the repo

`git clone git@github.com:ELDAELRA/trsproc.git`

### Create your python environment

#### Pip

- `python3 -m venv .venv && source .venv/bin/activate`
- `pip install -e '.[dev]'`

> [!NOTE]
> `pip install -e`  builds the package in editable mode, which means you won't have to re-build to sync your changes
>
> `pip install '.[dev]'` installs the optional dev dependencies defined in the `pyproject.toml` (currently ruff and pytest)

#### uv (simpler & faster)

`uv sync --extra dev`

### Create your branch

First checkout to dev
`git checkout dev`
And then create your feature branch from dev
`git checkout -b feat/my-feature`

### Get your hands on some test files

I advise you to copy the tests from a command in the root folder to make testing and debugging your changes easier. the vsi input folder is a good one because it has both trs and audio files.
You could run for example
`mkdir my-feature && cp tests/data/vsi/input/* my-feature`

## Develop your feature

Now the fun part begins!

> [!TIP]
> If you are not familiar with the Transcription class, play around with it in a REPL environment, like a jupyter notebook. The main entrypoint is the `new_parser.parse_trs_file` function.
>
> Avoid using AI until you are familiar with the codebase. If there's a feature or implementation you don't understand, you can always ask the maintainers

> [!CAUTION]
> Try to make your commits as atomic and descriptive as possible. In the commit description, try explaining what you did, and why you did it the way you did

## Submit your changes

### Check tests pass

Before submitting a PR, make sure all the tests still pass with `pytest`
If you implement a new feature, you should also write new tests for it

### Lint and format your code

`ruff check --fix`
`ruff format`

### Push your code

`git push --set-upstream origin my-branch-name`

Head over to github, and open your PR. If your PR is related to an issue, mention it in your message (for instance "This PR fixes #37")
Just like your commit messages, make your PR description as thorough as possible. Don't hesitate to repeat what you said in your commit messages in your PR again.

> [!Caution]
> Github will by default suggest merging on main, since it is the default branch. Make sure you change it and merge on dev instead.
