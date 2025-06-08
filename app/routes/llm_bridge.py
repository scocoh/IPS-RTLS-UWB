# Name: llm_bridge.py
# Version: 0.1.0
# Created: 250531
# Modified: 250531
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: TETSE Reusable Library
# Location: /home/parcoadmin/parco_fastapi/app/routes/llm_bridge.py
# Role: Backend
# Status: Active
# Dependent: TRUE

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ OPENAI_API_KEY is missing from .env file")

client = OpenAI(api_key=api_key)

def ask_openai(prompt: str, model: str = "gpt-4", temperature: float = 0.7) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains sensor events in plain English."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API error: {str(e)}"

#future plans
# Adding logging (e.g. logger.info(prompt)).
# Supporting function-calling (OpenAI’s function-calling interface).
# Letting ask_openai() optionally accept a list of messages (instead of one prompt).