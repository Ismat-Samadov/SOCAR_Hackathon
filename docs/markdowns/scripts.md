# Scripts Directory

One-time utility scripts for SOCAR Hackathon project.

## Available Scripts

### 📊 Data Management

#### `check_pinecone.py`
Check Pinecone vector database status and statistics.

```bash
python scripts/check_pinecone.py
```

**Output:**
- Total vector count
- Index dimensions
- Namespaces (if any)
- Connection status

#### `clear_pinecone.py`
Clear all data from Pinecone index before re-ingestion.

```bash
python scripts/clear_pinecone.py
```

**⚠️ WARNING**: This deletes ALL vectors! Requires typing 'DELETE' to confirm.

**Use case:**
- Before re-ingesting documents with new chunking strategy
- Testing with fresh data
- Cleaning up after experiments

### 🤖 Azure OpenAI

#### `list_azure_models.py`
List all deployed Azure OpenAI models.

```bash
python scripts/list_azure_models.py
```

**Output:**
- Vision models (GPT-4.1, GPT-5, Claude, etc.)
- Text models (Llama, DeepSeek, etc.)
- Total count and categorization

**Use case:**
- Verify which models are deployed
- Check model availability before updating notebooks
- Debugging 404 errors

## Setup

All scripts use environment variables from `.env` file:

```bash
# Required in .env
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=hackathon
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
```

## Dependencies

Scripts use the same dependencies as the main project:
- `python-dotenv` - Environment variables
- `pinecone-client` - Vector database
- `openai` - Azure OpenAI

Install from project root:
```bash
pip install -r notebooks/requirements.txt
```

## Common Workflows

### Re-ingesting Documents

```bash
# 1. Check current data
python scripts/check_pinecone.py

# 2. Clear existing data
python scripts/clear_pinecone.py

# 3. Run ingestion script (not included - create as needed)
# python scripts/ingest_documents.py

# 4. Verify new data
python scripts/check_pinecone.py
```

### Verifying Model Availability

```bash
# List all deployed models
python scripts/list_azure_models.py

# Check if specific model exists in output
python scripts/list_azure_models.py | grep "Llama-3.2-Vision"
```

## Adding New Scripts

When creating new scripts:
1. Add descriptive docstring at top
2. Use environment variables from `.env`
3. Include error handling with helpful messages
4. Update this README with usage instructions
5. Follow existing naming convention: `verb_noun.py`

## Examples

### Safe Pinecone Cleanup
```python
# First check what's there
$ python scripts/check_pinecone.py
Total Vectors: 1,300
Dimensions: 1024

# Then clear if needed
$ python scripts/clear_pinecone.py
⚠️  WARNING: This will delete ALL 1,300 vectors!
Type 'DELETE' to confirm: DELETE
✅ Deletion completed!
```

### Check Vision Models
```python
$ python scripts/list_azure_models.py

🖼️  Vision Models (6):
   ✅ gpt-4.1
   ✅ gpt-5
   ✅ gpt-5-mini
   ✅ claude-sonnet-4-5
   ✅ claude-opus-4-1
   ✅ Phi-4-multimodal-instruct
```
