import functions_framework
import google.generativeai as genai
import os
from vertexai.preview.generative_models import Tool
from vertexai.preview import rag


def retrieve_tool():
    # Create a RAG retrieval tool
    rag_retrieval_tool = Tool.from_retrieval(
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus="projects/customerserviceapp-432018/locations/us-central1/ragCorpora/8142508126285856768",
                        rag_corpus="projects/customerserviceapp-432018/locations/us-central1/ragCorpora/4611686018427387904",
                    )
                ],
                similarity_top_k=3,  # Optional
                vector_distance_threshold=0.5,  # Optional
            ),
        )
    )
    return rag_retrieval_tool

@functions_framework.http
def run_inference(request):
    request_json = request.get_json(silent=True)
    genai.configure(api_key="AIzaSyALbgZnPjprasq61lE2nRl-90pPasZisto")
    rag_retrieval_tool = retrieve_tool()
    if request_json and 'prompt' in request_json:
        prompt = request_json['prompt']
        if "history" in request_json:
            history = request_json["history"]
        else:
            history = []
        model = genai.GenerativeModel('gemini-1.5-flash-001', tools=[rag_retrieval_tool])
        model.start_chat(history)
        generated = model.send_message(prompt)
        response = generated.text
        print(response)
    else:
        response = 'World'
    return '{}!'.format(response)


# import functions_framework
# import google.generativeai as genai
# import os

# @functions_framework.http
# def run_inference(request):
#     request_json = request.get_json(silent=True)
#     genai.configure(api_key="AIzaSyALbgZnPjprasq61lE2nRl-90pPasZisto")
    
#     if request_json and 'prompt' in request_json:
#         prompt = request_json['prompt']
#         model = genai.GenerativeModel('gemini-1.0-pro-latest')
#         generated = model.generate_content(prompt)
#         response = generated.text
#         print(response)
#     else:
#         response = 'World'
#     return '{}!'.format(response)
