import uuid
import chromadb
from chromadb.utils import embedding_functions
chroma_client = chromadb.PersistentClient(path="./DB")

embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L12-v2"
)

working_context = chroma_client.get_or_create_collection(name="memories",  embedding_function=embedding_model)

def print_memories(memories):
    memories_string = "### Inserted memories:\n"
    memories_string +=  "\n".join([f"- {memory}" for memory in memories])
    print(memories_string, "\n")


def results_to_string(results):
    result_string = "### Memory recall results:\n"
    result_string += "\n".join([f"- {entry['document']}" for entry in results])
    print(result_string, "\n")
    return result_string

def process_results(results):
    return [
        {
            "id": results["ids"][0][i], 
            "document": results["documents"][0][i] 
        }
        for i in range(len(results["ids"][0]))
    ]


def insert_memories(memories):
    working_context.add(
        documents=memories,
        ids=[f"{uuid.uuid4()}" for _ in range(len(memories))]
    )
    print_memories(memories)
    

def recall_memories(query, num_results=2):
    print(f"recall: {query}")
    if num_results is None:
        num_results = 2

    results = working_context.query(
        query_texts = [query], 
        n_results = num_results
    )
    processed_results = process_results(results)
    return results_to_string(processed_results)
    