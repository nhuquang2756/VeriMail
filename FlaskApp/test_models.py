"""
Quick test to verify model predictions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core import ModelManager

# Initialize model manager
model_manager = ModelManager()

# Test spam message (should predict SPAM)
spam_message = "Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005. Text FA to 87121 to receive entr code"

# Test ham message (should predict HAM)
ham_message = "Hi, how are you doing today? I hope you're having a great day!"

print("=" * 80)
print("TESTING ALL MODELS")
print("=" * 80)

# Get all available models
models = model_manager.get_available_models()

print(f"\nTotal models available: {len(models)}\n")

print("SPAM MESSAGE TEST (Should predict SPAM):")
print(f"Message: {spam_message}\n")
for model in models:
    try:
        result = model_manager.predict_single(spam_message, model)
        print(f"  {model}: {result}")
    except Exception as e:
        print(f"  {model}: ERROR - {e}")

print("\n" + "=" * 80)
print("HAM MESSAGE TEST (Should predict HAM):")
print(f"Message: {ham_message}\n")
for model in models:
    try:
        result = model_manager.predict_single(ham_message, model)
        print(f"  {model}: {result}")
    except Exception as e:
        print(f"  {model}: ERROR - {e}")

print("\n" + "=" * 80)
print("MODEL INFO:")
print("=" * 80)
for model in models:
    try:
        info = model_manager.get_model_info(model)
        print(f"\n{model}:")
        print(f"  File: {info['file']}")
        print(f"  Exists: {info['exists']}")
        print(f"  Size: {info['size_mb']:.2f} MB")
    except Exception as e:
        print(f"  {model}: ERROR - {e}")
