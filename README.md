# carechat-planer
株式会社CareChatのケアプランナー作成botの実装

## Deploy

Build and push
```
IMAGE_NAME=gcr.io/${PROJECT_ID}/planer_bot:latest
docker buildx build --platform linux/amd64 -t ${IMAGE_NAME} --target runner .
docker push ${IMAGE_NAME}
```

```
gcloud run deploy your-app-service \
  --image ${IMAGE_NAME} \
  --region asia-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --service-account planer-bot-service-account@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET},LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN},OPENAI_API_KEY=${OPENAI_API_KEY},BASIC_AUTH_PASSWORD=${BASIC_AUTH_PASSWORD}
```

## Configuration (First time only)
```
gcloud iam service-accounts create planer-bot-service-account \
  --display-name "Planer-bot Cloud Run Service Account"
```

```
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:planer-bot-service-account@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

```
gcloud auth configure-docker
```
