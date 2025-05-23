# carechat-planer

株式会社CareChatのケアプランナー作成botの実装

## Deploy

Set up your environment variables and credentials

```sh
source set_env.sh
gcloud auth login
```

Build and push

```sh
IMAGE_NAME=gcr.io/${PROJECT_ID}/planer_bot:latest
docker buildx build --platform linux/amd64 -t ${IMAGE_NAME} --target runner .
docker push ${IMAGE_NAME}
```

Deploy to Cloud Run

```sh
gcloud run deploy planer-bot-service \
  --image ${IMAGE_NAME} \
  --region asia-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --service-account planer-bot-service-account@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET},LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN},OPENAI_API_KEY=${OPENAI_API_KEY},BASIC_AUTH_PASSWORD=${BASIC_AUTH_PASSWORD}
```

## Configuration (First time only)

```sh
gcloud iam service-accounts create planer-bot-service-account \
  --display-name "Planer-bot Cloud Run Service Account"
```

```sh
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:planer-bot-service-account@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

docker の認証

`failed to authorize: failed to fetch anonymous token: unexpected status from GET request to https://gcr.io/v2/token?scope=repository%3Acarechat-prod%2Fgcr.io%2Fplaner_bot%3Apull&scope=repository%3Acarechat-prod%2Fplaner_bot%3Apull%2Cpush&service=gcr.io: 403 Forbidden`
```sh
gcloud auth configure-docker
```


After first time deploy, run once

```sh
gcloud run services add-iam-policy-binding planer-bot-service \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region=asia-northeast1
```
