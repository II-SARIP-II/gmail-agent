from ollama import chat







response = chat(
    model="mistral",
    messages=[{'role': 'user', 'content': 'shut up!'}],
)
print(response.message.content)
'''
class LLMAnalyst():
    self.model = "mistral:7b"

    def 
    response = chat(
    model='mistral',
    messages=[{'role': 'user', 'content': 'Hello!'}],
)
print(response.message.content)
'''
