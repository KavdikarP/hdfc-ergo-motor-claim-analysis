#!/bin/bash
# Go to root dir
# cd $(dirname $0)/..

# Variables
export PROJECT_ID=ccinsights3
export CLOUDRUN_SERVICE_NAME=hdfc-ergo-claim-analysis
export CLOUDRUN_SERVICE_IMAGE_NAME=us-central1-docker.pkg.dev/$PROJECT_ID/$CLOUDRUN_SERVICE_NAME/$CLOUDRUN_SERVICE_NAME:latest

# Setup
gcloud config set project $PROJECT_ID
gcloud auth application-default set-quota-project $PROJECT_ID

# Build image
gcloud builds submit --tag $CLOUDRUN_SERVICE_IMAGE_NAME .

# Deploy image
gcloud run deploy $CLOUDRUN_SERVICE_NAME \
    --image $CLOUDRUN_SERVICE_IMAGE_NAME \
    --region us-central1 \
    --port 8501 --allow-unauthenticated
