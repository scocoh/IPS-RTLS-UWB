# Name: test_openai_tetse.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/test_openai_tetse.py
# Role: Backend
# Status: Active
# Dependent: TRUE

# test_openai_tetse.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-4",  # or "gpt-3.5-turbo" if preferred
        messages=[
            {"role": "system", "content": "You are an assistant to the TETSE event engine."},
            {"role": "user", "content": "Explain the value of combining TETSE with OpenAI models."}
        ],
        temperature=0.7,
        max_tokens=250
    )

    print("✅ Response from OpenAI:")
    print(response.choices[0].message.content)

except Exception as e:
    print("❌ Error calling OpenAI:\n")
    print(e)
