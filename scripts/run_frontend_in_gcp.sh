INSTANCE_NAME="instance-1"
REGION=us-central1
ZONE=us-central1-a
PROJECT_NAME="searchengine-337218"
IP_NAME="$PROJECT_NAME-ip"
GOOGLE_ACCOUNT_NAME="itda"

# 0. Install Cloud SDK on your local machine or using Could Shell
# check that you have a proper active account listed
gcloud auth list 
# check that the right project and zone are active
gcloud config list
# if not set them
# gcloud config set project $PROJECT_NAME
# gcloud config set compute/zone $ZONE

# 1. Set up public IP
gcloud compute addresses create $IP_NAME --project=$PROJECT_NAME --region=$REGION
gcloud compute addresses list
# note the IP address printed above, that's your extrenal IP address.
# Enter it here: 
