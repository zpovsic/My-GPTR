from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    response = client.chat.completions.create(
        model='gpt-5-mini',
        messages=[{'role': 'user', 'content': 'hi'}]
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f'ERROR for gpt-5-mini: {e}')
try:
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'hi'}]
    )
    print(f'gpt-4o-mini response: {response.choices[0].message.content}')
except Exception as e:
    print(f'ERROR for gpt-4o: {e}')
