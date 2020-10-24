# hegemone-public
Proof-of-concept for executing Jupyter notebooks using Papermill in Docker.

## Cloud Run service
In order to deploy a service for executing Jupyter notebooks on Cloud Run:
1. `make build` builds the docker image
1. `make deploy` deploys the image to Cloud Run

Run `make test` to validate, if the service is running correctly.

### Executing a Jupyter notebook using Cloud Run service
To execute a template notebook make sure to provide a valid GCS bucket in 
`parameters.yaml`, and run:
```bash
python run.py ./notebooks/templates/00-ww-sample-template.ipynb -gcp
```