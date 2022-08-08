# DSWx-Jupyter-Validation-Dataset-Generation

This is a prototype to (begin to) demonstrate the semi-automated generation of DSWx validation datasets derived from Planet Imagery. For each planet image:

1.  We use an auxiliary dataset such as Peckel occurence data or Sentinel-2 LULC data reprojected into the planet reference frame to train a basic ML model to obtain class labels calibrated with the auxiliary data.
2.  We update classification labels by hand. This step is currently ommitted.

For each step, we store related data in s3. Currently, we are using papermill to orchestrate template notebooks. We may transition to pure python functions for more effective version control and testing, in which case we would have to change the name of the repository.

Additionally, for demonstration purposes, we will show how to verify requirements using the ML generated dataset against provisional products in addition to other accuracy statistics.

## Setup

An env file should have the following information:

```
PLANET_API_KEY='<API_KEY>'
ES_USERNAME='<JPL USERNAME>'
ES_PASSWORD='<JPL PASSWORD>'
```

To the ~/.aws/credentials file:

```
[default]
aws_access_key_id = ''
aws_secret_access_key = ''
```

Geopandas expects these fields even if they are not filled in.

## Install
It is recommended to install `mamba` in the user's base environment to speed up the installation process:

`conda install -c conda-forge mamba`

From this repo:

1. `mamba env create -f environment.yml`
3. `conda activate dswx_val`

## To run

`python run_pipeline.py`

## Known issues

+ The papermill orchestration has the following error `OSError: [Errno 24] Too many open files`.

## Contributing

Create a branch from dev and create a pull request. Have another member review. Make sure to clear your outputs for better version control.
