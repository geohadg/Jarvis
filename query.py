from ollama import generate
import sys
from configparser import ConfigParser
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

config = ConfigParser()
config.read("assistantconfig.ini")

model = config['DEFAULTS']['ollamamodel']
vectordatabasepath = config['DEFAULTS']['vectordatabasepath']

def model_query(query: str) -> None:
    embeddings = OllamaEmbeddings(model=model)
    vectordb = Chroma(collection_name="trainingdata", persist_directory=vectordatabasepath, embedding_function=embeddings)
    
    formattedquery = generate(model=model, prompt=f"You are a helpful assistant that turns raw user queries into a version optimized for retreiving the most relevant documents. When a user sends a message, respond with an optimized version of their query and nothing else. Now do it to the following query: {query}")
    fq = str(formattedquery['response'])
    # print(fq)
    # print(query)
    # retriever = vectordb.as_retriever()
    # context = retriever.invoke(query)
    # context = vectordb.similarity_search_by_vector(embedding=embeddings.embed_query(query), k=1)
    context = vectordb.similarity_search(query=fq, k=50)
    # for i in context:
    #     print(f"{i.page_content}")
    #     print("\n")

    # print(f"\n{context[0]}")
    # print(context[0].page_content)
    # print(embedded_query)
    
    # print("")
    # # query block here
    for part in generate(model=model, prompt=f"Answer the question {query} with the following context: {context[0].page_content}. If you dont know dont from the context, just answer the way you normally would", stream=True):
        print(part['response'], end='', flush=True)
    
    print("\n----------------------------------------------------------------------------------------")
    print(f"\nContext extracted from file: {context[0].metadata['path']}")

if __name__ == "__main__":
    try:
        model_query(sys.argv[1])

    except Exception as e:
        print(f'\nQuery failed: {e}')