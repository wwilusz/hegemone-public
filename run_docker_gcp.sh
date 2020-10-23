#!/bin/bash

docker run -ti \
-e "GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/FILE_NAME.json" \
-v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/FILE_NAME.json:ro \
--rm \
--name gcp \
hegemone \
bash
