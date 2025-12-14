"""
List all deployed Azure OpenAI models
Useful for verifying available models
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

def list_azure_models():
    """List all deployed Azure OpenAI models"""

    try:
        client = AzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        )

        print("="*80)
        print("AZURE OPENAI DEPLOYED MODELS")
        print("="*80)

        # List models
        models = client.models.list()

        print(f"\n📊 Total Models: {len(list(models))}")
        print(f"\nDeployed Models:")
        print("-" * 80)

        model_list = []
        for model in models:
            model_list.append({
                'id': model.id,
                'created': model.created if hasattr(model, 'created') else 'N/A'
            })

        # Sort by id
        model_list.sort(key=lambda x: x['id'])

        # Categorize models
        vision_models = []
        text_models = []

        for model in model_list:
            model_id = model['id']
            if any(keyword in model_id.lower() for keyword in ['vision', 'multimodal', 'gpt-4.1', 'gpt-5', 'claude']):
                vision_models.append(model_id)
            else:
                text_models.append(model_id)

        print(f"\n🖼️  Vision Models ({len(vision_models)}):")
        for model_id in vision_models:
            print(f"   ✅ {model_id}")

        print(f"\n📝 Text Models ({len(text_models)}):")
        for model_id in text_models:
            print(f"   ✅ {model_id}")

        print("\n" + "="*80)

    except Exception as e:
        print("="*80)
        print("AZURE OPENAI CONNECTION ERROR")
        print("="*80)
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("  1. AZURE_OPENAI_API_KEY in .env file")
        print("  2. AZURE_OPENAI_ENDPOINT in .env file")
        print("  3. API version compatibility")

if __name__ == "__main__":
    list_azure_models()
