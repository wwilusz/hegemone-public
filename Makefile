PROJECT_ID=$(shell gcloud config get-value core/project)
all:
	@echo "build  - Build the docker image"
	@echo "deploy - Deploy the image to Cloud Run (or locally)"
	@echo "clean  - Clean up created artifacts"
	@echo "test   - Call the Cloud Run (or local) service with a sample command"
	@echo "If appended with '-local' postfix, all commands will be run locally"

deploy:
	gcloud run deploy cloud-run-hegemone \
		--image gcr.io/$(PROJECT_ID)/cloud-run-hegemone \
		--max-instances 1 \
		--platform managed \
		--region us-central1 \
		--no-allow-unauthenticated

deploy-local:
	docker run \
		-e "PORT=5000" \
		-e "GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/FILE_NAME.json" \
		-v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/FILE_NAME.json:ro \
		--publish 5000:5000 \
		--name local-hegemone-service \
		--rm \
		local-hegemone

build:
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/cloud-run-hegemone

build-local:
	docker build -t local-hegemone .

clean:
	-gcloud container images delete gcr.io/$(PROJECT_ID)/cloud-run-hegemone --quiet
	-gcloud run services delete cloud-run-hegemone \
		--platform managed \
		--region us-central1 \
		--quiet

clean-local:
	docker rmi --force local-hegemone

test:
	@echo "Testing Cloud Run hegemone service"
	@url=$(shell gcloud run services describe cloud-run-hegemone --format='value(status.url)' --region us-central1 --platform managed); \
	token=$(shell gcloud auth print-identity-token); \
	curl --request POST \
  		 --header "Authorization: Bearer $$token" \
  		 --header "Content-Type: text/plain" \
  		 $$url/exec \
  		 --data-binary "python ./run.py -h"

test-local:
	@echo "Testing local hegemone service"
	curl --request POST \
		 --header "Content-Type: text/plain" \
  		 127.0.0.1:5000/exec \
  		 --data-binary "python ./run.py -h"