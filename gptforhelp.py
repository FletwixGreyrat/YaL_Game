
import os
os.system('pip install -U g4f')
import g4f
request = ''''''

response = g4f.ChatCompletion.create(
    model=g4f.models.gpt_35_turbo,
    messages=[{'role': 'user', "content": request}]
)

with open('response.txt', 'w') as file:
    file.write(response)