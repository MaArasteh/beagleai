import ollama

response = ollama.chat(model='tinyllama', messages=[
  {
    'role': 'user',
    'content': 'How to compress files in Windows',
  },
])
print(response['message']['content'])