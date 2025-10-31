# Usage

## Installation

You can install agriphyto-schema via [uv](https://docs.astral.sh/uv/):

```shell script
uv install agriphyto_schema
```

## Using the project

### Running the application

Pre-requisite:
v
 - Make sure you have installed the package as per the
[Installation](#installation) instructions.

```shell
uv run streamlit run agriphyto_schema/app/app.py
```

### Creating appropriate data schemas for the application

The application relies on pre-defined data schemas for each dictionary. These schemas are generated from the raw dictionary files with two steps:

NB: The detailed commands are detailed in the CLI [CLI documentation](https://straymat.github.io/agriphyto-schema/cli-usage.html).

#### 1 - Parse a dictionary

Parse the dictionary file and create a pandera schema file for each table in the raw dictionnary file in
  `data/schemas/{DICO_NAME}.json`. This step also extracts nomenclatures for each variable in the dictionary. It stores them in one nomenclature file with append mode at `data/nomenclatures/all_nomenclatures.json`.

```shell script
uv run python bin/cli.py parse --dico <DICO_NAME> # eg. RA2020
```

#### Aggregate dictionaries

It aggregates all available pandera schemas in the "data/schema" folder into one csv file for the application.

```shell script
uv run python bin/cli.py aggregate --dico <DICO_NAME> # eg. RA2020
```
## Deployment of the application on Onyxia (SSPCloud)

The application is deployed on Onyxia (SSPCloud) using kubernetes and helm, following [the online instructions](https://github.com/InseeFrLab/sspcloud-tutorials/blob/main/deployment/shiny-app.md) (adapted from shiny).

The [deployment code for the helm chart](https://github.com/straymat/agriphyto-schema-deployment) inherits from the (poorly named) [shiny helm chart](https://github.com/InseeFrLab/helm-charts/tree/master/charts/shiny) built by Insee. No modification to this dependency is needed since it should work for multiple web applications frameworks. The chart is pulling the docker image from the public docker hub repository [straymat/agriphyto-dico-app](https://hub.docker.com/r/straymat/agriphyto-dico-app).

The application should be accessible at : https://agriphyto-dictionnaire-donnees.lab.sspcloud.fr/

## Development

### Package and Dependencies Installation

Make sure you have Python 3.13+ and [uv](https://docs.astral.sh/uv/)
installed and configured.

To install the package and all dev dependencies, run:

```shell script
make install
```


### Testing

We use [pytest](https://pytest.readthedocs.io/) for our testing framework.

To invoke the tests, run:

```shell script
make test
```

### Code Quality

We use [pre-commit](https://pre-commit.com/) for our code quality
static analysis automation and management framework.

To invoke the analyses and auto-formatting over all version-controlled files, run:

```shell script
ruff check . -a  # Applies all safe autofixes
```

> 🚨 **Danger**
> CI will fail if either testing or code quality fail,
> so it is recommended to automatically run the above locally
> prior to every commit that is pushed.

#### Automate via Git Pre-Commit Hooks

To automatically run code quality validation on every commit (over to-be-committed
files), run:

```shell script
make install-pre-commit
```

> ⚠️ Warning !
> This will prevent commits if any single pre-commit hook fails
> (unless it is allowed to fail)
> or a file is modified by an auto-formatting job;
> in the latter case, you may simply repeat the commit and it should pass.


### Documentation

```shell script
make docs-clean docs-html
```

> 📝 **Note**
> This command will generate html files in `docs/_build/html`.
> The home page is the `docs/_build/html/index.html` file.
