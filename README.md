# acme-prefect

Sample project using [`prefect`](https://www.prefect.io/) orchestration library and [`acme-portal-sdk`](https://github.com/blackwhitehere/acme-portal-sdk) to manage deployments via [`acme-portal`](https://github.com/blackwhitehere/acme-portal) VSCode extension.

# Features

* Showcases use of `prefect` library for workflow orchestration
* Showcases how `acme-portal-sdk` can be used to provide data and actions for `acme-portal` `VSCode` extension


# Dev environment

The project comes with a python development environment.
To generate it, after checking out the repo run:

    chmod +x create_env.sh

Then to generate the environment (or update it to latest version based on state of `uv.lock`), run:

    ./create_env.sh

This will generate a new python virtual env under `.venv` directory. You can activate it via:

    source .venv/bin/activate

If you are using VSCode, set to use this env via `Python: Select Interpreter` command.

# Project template

This project has been setup with `acme-project-create`, a python code template library.

# Required setup post template use

* Enable GitHub Pages to be published via [GitHub Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow) by going to `Settings-->Pages-->Source`
* Create `release` environment for [GitHub Actions](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment#creating-an-environment) to enable uploads of the library to PyPi
* Setup auth to PyPI for the GitHub Action implemented in `.github/workflows/release.yml` via [Trusted Publisher](https://docs.pypi.org/trusted-publishers/adding-a-publisher/) `uv publish` [doc](https://docs.astral.sh/uv/guides/publish/#publishing-your-package)
* Once you create the python environment for the first time add the `uv.lock` file that will be created in project directory to the source control and update it each time environment is rebuilt
* In order not to replicate documentation in `docs/docs/index.md` file and `README.md` in root of the project setup a symlink from `README.md` file to the `index.md` file.
To do this, from `docs/docs` dir run:

    ln -sf ../../README.md index.md