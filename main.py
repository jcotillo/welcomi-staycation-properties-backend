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
display_name = os.getenv('RAG_DISPLAY_NAME')
paths = [os.getenv('LANDING_PAGE_PATH')]  # Supports Google Cloud Storage and Google Drive Links

# Create RagCorpus
# Configure embedding model, for example "text-embedding-004".
embedding_model_config = rag.EmbeddingModelConfig(
    publisher_model="publishers/google/models/text-embedding-004"
)

rag_corpus = rag.create_corpus(
    display_name=display_name,
    embedding_model_config=embedding_model_config,
)

# Import Files to the RagCorpus
response = rag.import_files(
    rag_corpus.name,
    paths,
    chunk_size=512,  # Optional
    chunk_overlap=100,  # Optional
    max_embedding_requests_per_min=900,  # Optional
)

# Enhance generation
# Create a RAG retrieval tool
rag_retrieval_tool = Tool.from_retrieval(
    retrieval=rag.Retrieval(
        source=rag.VertexRagStore(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=rag_corpus.name,  # Currently only 1 corpus is allowed.
                    # Supply IDs from `rag.list_files()`.
                    # rag_file_ids=["rag-file-1", "rag-file-2", ...],
                )
            ],
            similarity_top_k=3,  # Optional
            vector_distance_threshold=0.5,  # Optional
        ),
    )
)
safety_config = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

LOG_NAME = "run_inference-cloudfunction-log"
logger = client.logger(LOG_NAME)

# Create a RAG retrieval tool
rag_retrieval_tool = Tool.from_retrieval(
    retrieval=rag.Retrieval(
        source=rag.VertexRagStore(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=rag_corpus.name,  # Currently only 1 corpus is allowed.
                    # Supply IDs from `rag.list_files()`.
                    # rag_file_ids=["rag-file-1", "rag-file-2", ...],
                )
            ],
            similarity_top_k=3,  # Optional
            vector_distance_threshold=0.5,  # Optional
        ),
    )
)

@functions_framework.http
def run_inference(request):
    request_json = request.get_json(silent=True)

    if request_json and "prompt" in request_json:
        prompt = request_json["prompt"]
        logger.log(f"Received request for prompt: {prompt}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        # model = GenerativeModel(model_name="gemini-1.5-flash-001")
        model = GenerativeModel(model_name="gemini-1.5-flash-001", tools=[rag_retrieval_tool])

        # Generate response
        response = model.generate_content(prompt, safety_settings=safety_config)

        prompt_response = response.text
    else:
        prompt_response = "No prompt provided."

    return json.dumps({"response_text": prompt_response})

