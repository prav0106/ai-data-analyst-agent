import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("\n" + "="*60)
print("✅ AVAILABLE MODELS FOR YOUR API KEY:")
print("="*60 + "\n")

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")

print("\n" + "="*60)