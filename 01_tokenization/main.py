import tiktoken
encoder = tiktoken.encoding_for_model("gpt-4o")

text = "Virat hits a six"
tokens = encoder.encode(text)

print("Tokens:", tokens)

Tokens= [60985, 266, 21571, 261, 7429]
decoded = encoder.decode(tokens)

print("Decoded Text:", decoded)