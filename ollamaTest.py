#!/usr/bin/env python3

import requests

try:
    response = requests.get("http://localhost:11434/api/tags")
    models = response.json().get('models', [])
    print(f"✓ Ollama is running! Found {len(models)} models:")
    for m in models:
        print(f"  - {m['name']}")
except:
    print("✗ Ollama not running. Run: ollama serve")
