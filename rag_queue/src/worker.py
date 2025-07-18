from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

print("Worker: Initializing connections...")
try:
    # Initialize the embedding model
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-large"
    )

    # Connect to the existing Qdrant collection
    vector_db = QdrantVectorStore.from_existing_collection(
        url="http://vector-db:6333",
        collection_name="AI-Crash-Report",
        embedding=embedding_model
    )
    print("Worker: Connection to Vector DB successful.")
except Exception as e:
    print(f"Worker: FATAL ERROR - Could not connect to Vector DB. {e}")
    vector_db = None


def process_query(query: str):
    """
    This function is executed by the RQ worker.
    It performs a similarity search and generates a response using an LLM.
    """
    if vector_db is None:
        return "Error: Worker could not connect to the vector database. Please check worker logs."

    print(f"Worker: Processing query: '{query}'")
    
    search_results = vector_db.similarity_search(query=query)
    context = "\n\n---\n\n".join(
        [f"Page Content: {result.page_content}\nSource: Page {result.metadata.get('page', 'N/A') + 1}" for result in search_results]
    )
    SYSTEM_PROMPT = f"""
        You are a helpful AI assistant who answers user questions based on the
        provided context from a PDF document.

        Your task is to synthesize the information from the context below to answer the user's query.
        You must only use the information from the provided context.
        When you answer, always cite the page number from the source so the user can find more details.

        Context:
        {context}
    """

    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ]
        )
        response = chat_completion.choices[0].message.content
        print(f"Worker: Successfully generated response for query: '{query}'")
        print(f"Response: '{response}'")
    except Exception as e:
        print(f"Worker: An error occurred while calling the OpenAI API: {e}")
        return "An error occurred while generating the response. Please check the worker logs."
