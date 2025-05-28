from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

text = "Virat hits a six"

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)

print("Vector Embeddings", response)
print(len(response.data[0].embedding))