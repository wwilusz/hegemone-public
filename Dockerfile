FROM jupyter/scipy-notebook

USER root

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

RUN apt-get update

RUN pip install --upgrade pip setuptools wheel

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY requirements.txt /project/

# Install dependencies.
RUN cd /project && pip install --pre -r requirements.txt

# Copy local code to the container image.
ENV PROJECT_HOME /project
WORKDIR $PROJECT_HOME
COPY . ./
