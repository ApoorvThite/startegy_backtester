import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_gpt(prompt: str, model="gpt-3.5-turbo", temperature=0.7) -> str:
    messages = [
        {"role": "system", "content": "You are an expert trading strategy assistant."},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response['choices'][0]['message']['content'].strip()
