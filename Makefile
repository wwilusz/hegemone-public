PROJECT_ID=$(shell gcloud config get-value core/project)
all:
	@echo "build  - Build the docker image"
	@echo "deploy - Deploy the image to Cloud Run"
	@echo "clean  - Clean up created artifacts"
	@echo "test   - Call the Cloud Run service with a sample command"

deploy:
	gcloud run deploy cloud-run-hegemone \
		--image gcr.io/$(PROJECT_ID)/cloud-run-hegemone \
		--max-instances 1 \
		--platform managed \
		--region us-central1 \
		--no-allow-unauthenticated

build:
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/cloud-run-hegemone

clean:
	-gcloud container images delete gcr.io/$(PROJECT_ID)/cloud-run-hegemone --quiet
	-gcloud run services delete cloud-run-hegemone \
		--platform managed \
		--region us-central1 \
		--quiet

test:
	@echo "Testing Cloud Run hegemone service"
	@url=$(shell gcloud run services describe cloud-run-hegemone --format='value(status.url)' --region us-central1 --platform managed); \
	token=$(shell gcloud auth print-identity-token); \
	curl --request POST \
  		 --header "Authorization: Bearer $$token" \
  		 --header "Content-Type: text/plain" \
  		 $$url/exec \
  		 --data-binary "python ./run.py -h"