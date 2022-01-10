gcloud compute instances delete -q $INSTANCE_NAME
gcloud compute instances list
gcloud compute firewall-rules delete -q default-allow-http-8080
gcloud compute addresses delete -q $IP_NAME --region $REGION