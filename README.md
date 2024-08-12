# Welcomi Staycation Properties Backend

This repository contains the backend code for the Welcomi Staycation Properties project. The main functionality is implemented in `main.py`, which is designed to be deployed as a Google Cloud Function.

## Features

- **Google Cloud Logging**: Logs are sent to Google Cloud Logging for monitoring and analysis.
- **Vertex AI Integration**: Utilizes Vertex AI for generative models and retrieval-augmented generation (RAG).
- **Environment Variables**: Configuration is managed through environment variables loaded from a `.env` file.

## Setup

### Prerequisites

- Python 3.7 or higher
- Google Cloud SDK
- A Google Cloud project with the necessary APIs enabled:
  - Cloud Functions
  - Vertex AI
  - Cloud Logging

### Installation

1. Clone the repository:
  ```sh
    git clone https://github.com/yourusername/welcomi-staycation-properties-backend.git
   cd welcomi-staycation-properties-backend
  ```

2. Create and activate a virtual environment:
  ```sh
  python3 -m venv venv
  source venv/bin/activate
  ```

3. Install the required packages:
  ```sh
   pip install -r requirements.txt
  ```

4. Create a .env file in the root directory and add the following environment variables:
  ```
  PROJECT_ID=your-google-cloud-project-id
  RAG_DISPLAY_NAME=your-rag-display-name
  LANDING_PAGE_PATH=your-landing-page-path
  RAG_ID=your-rag-id
  ```

### Deployment

1. Deploy the Cloud Function using the Google Cloud SDK:
  ```sh
  gcloud functions deploy run_inference \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --project $PROJECT_ID
  ```

### Usage

Once deployed, the Cloud Function can be triggered via an HTTP request. The request should be a JSON payload with the following structure:
``` json
{
  "prompt": "Your prompt here",
  "history": [
    {
      "role": "user",
      "message": "Previous message"
    },
    {
      "role": "assistant",
      "message": "Previous response"
    }
  ]
}
```
### Example Request
```
curl -X POST https://YOUR_CLOUD_FUNCTION_URL \
-H "Content-Type: application/json" \
-d '{
  "prompt": "Tell me about the weather today.",
  "history": [
    {
      "role": "user",
      "message": "Hello!"
    },
    {
      "role": "assistant",
      "message": "Hi! How can I help you today?"
    }
  ]
}'
```
### Example Response
```
{
  "response_text": "The weather today is sunny with a high of 75 degrees."
}
```

