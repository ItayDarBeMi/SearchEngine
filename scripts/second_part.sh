INSTANCE_NAME="instance-1"
REGION=us-central1
ZONE=us-central1-a
PROJECT_NAME="searchengine-337218"
INSTANCE_IP="35.223.63.141"

# 2. Create Firewall rule to allow traffic to port 8080 on the instance
gcloud compute firewall-rules create default-allow-http-8080 \
  --allow tcp:8080 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server

# 3. Create the instance. Change to a larger instance (larger than e2-micro) as needed.
gcloud compute instances create $INSTANCE_NAME \
  --zone=$ZONE \
  --machine-type=e2-highmem-2 \
  --network-interface=address=$INSTANCE_IP,network-tier=PREMIUM,subnet=default \
  --metadata-from-file startup-script=startup_script_gcp.sh \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --tags=http-server \
  --boot-disk-size "200GB"
# monitor instance creation log using this command. When done (4-5 minutes) terminate using Ctrl+C
gcloud compute instances tail-serial-port-output $INSTANCE_NAME --zone $ZONE

# 4. Secure copy your app to the VM

## 5. SSH to your VM and start the app
#gcloud compute ssh $GOOGLE_ACCOUNT_NAME@$INSTANCE_NAME
#python3 search_frontend_1.0.py
#