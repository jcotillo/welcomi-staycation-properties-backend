import os
import json

from google.cloud import logging
import functions_framework
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Tool
from vertexai.preview import rag
from vertexai.preview import generative_models
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env file

PROJECT_ID = os.getenv('PROJECT_ID')
LOCATION = "us-central1"
client = logging.Client(project=PROJECT_ID)
client.setup_logging()

# Create rag
def _create_rag_tool():
    display_name = os.getenv('RAG_DISPLAY_NAME')
    paths = [os.getenv('LANDING_PAGE_PATH')]  # Supports Google Cloud Storage and Google Drive Links
    
    # Configure embedding model, for example "text-embedding-004".
    embedding_model_config = rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-004"
    )

    rag_corpus = rag.create_corpus(
        display_name=display_name,
        embedding_model_config=embedding_model_config,
    )

    # Import Files to the RagCorpus
    rag.import_files(
        rag_corpus.name,
        paths,
        chunk_size=512,  # Optional
        chunk_overlap=100,  # Optional
        max_embedding_requests_per_min=900,  # Optional
    )

def retrieve_tool():
    # Create a RAG retrieval tool
    rag_retrieval_tool = Tool.from_retrieval(
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=os.getenv('RAG_ID'),
                    )
                ],
                similarity_top_k=3,  # Optional
                vector_distance_threshold=0.5,  # Optional
            ),
        )
    )
    return rag_retrieval_tool

LOG_NAME = "run_inference-cloudfunction-log"
logger = client.logger(LOG_NAME)

@functions_framework.http
def run_inference(request):
    request_json = request.get_json(silent=True)

    if request_json and "prompt" in request_json:
        prompt = request_json["prompt"]
        if "history" in request_json:
            history = request_json["history"]
        else:
            history = []
        logger.log(f"Received request for prompt: {prompt}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        rag_retrieval_tool = retrieve_tool()
        model = GenerativeModel(model_name="gemini-1.5-flash-001", tools=[rag_retrieval_tool])

        # Generate response
        model.start_chat(history=history)
        response = model.send_message(prompt)
        prompt_response = response.text
    else:
        prompt_response = "No prompt provided."

    return json.dumps({"response_text": prompt_response})

