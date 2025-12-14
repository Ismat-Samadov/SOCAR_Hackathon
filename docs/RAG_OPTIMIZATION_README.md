# RAG Pipeline Optimization - Complete Guide

## Overview

This comprehensive benchmark tests **EVERY component** of your RAG pipeline to maximize LLM Judge score (30% of hackathon total).

## What Gets Tested

### 1. 📚 Embedding Models (5 models)
Vector representations for semantic search:

| Model | Dimensions | Speed | Quality | Notes |
|-------|-----------|-------|---------|-------|
| **BAAI/bge-large-en-v1.5** | 1024 | Medium | ⭐⭐⭐⭐⭐ | Current - best quality |
| **BAAI/bge-base-en-v1.5** | 768 | Fast | ⭐⭐⭐⭐ | Faster alternative |
| **intfloat/multilingual-e5-large** | 1024 | Medium | ⭐⭐⭐⭐⭐ | Multi-language optimized |
| **paraphrase-multilingual-mpnet** | 768 | Fast | ⭐⭐⭐⭐ | Good for Azerbaijani/Russian |
| **all-MiniLM-L6-v2** | 384 | Very Fast | ⭐⭐⭐ | Lightweight |

**Note**: Only 1024-dim models work with your existing Pinecone index!

### 2. 🔎 Retrieval Strategies (7 strategies)

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| **vanilla_k3** | Top-3 documents | Current setup, baseline |
| **vanilla_k5** | Top-5 documents | More context |
| **vanilla_k10** | Top-10 documents | Maximum context |
| **threshold_0.7** | Filter by similarity >0.7 | Quality over quantity |
| **mmr_balanced** | Diversity + relevance (λ=0.5) | Avoid redundant docs |
| **mmr_diverse** | More diversity (λ=0.3) | Very different perspectives |
| **reranked_k3** | Two-stage: retrieve 20 → rerank → top 3 | Best quality |

**MMR** = Maximal Marginal Relevance (balances relevance vs diversity)
**Reranking** = Use cross-encoder for better ordering

### 3. 🤖 LLM Models (5 models)

- **Llama-4-Maverick-17B** (open-source, architecture score)
- **DeepSeek-R1** (reasoning model)
- **GPT-4.1, GPT-5, GPT-5-mini**
- **Claude-Sonnet-4.5** (best quality)

### 4. 💬 Prompting Strategies (4 strategies)

| Strategy | Focus | When to Use |
|----------|-------|-------------|
| **baseline** | Simple context + question | Quick baseline |
| **citation_focused** | Emphasizes source references | Better citation scores |
| **step_by_step** | Chain-of-thought reasoning | Complex questions |
| **few_shot** | Includes example Q&A | Consistent formatting |

## LLM Judge Evaluation Criteria

Your score is calculated as:
```
LLM Judge Score = (Accuracy × 35%) + (Citation × 35%) + (Completeness × 30%)
```

### Components:
- **Accuracy** (35%): How correct is the answer?
- **Citation Quality** (35%): Proper PDF names + page numbers?
- **Completeness** (30%): Thorough and well-formed?

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements_rag_optimization.txt
```

### 2. Ensure Data is Ready
You need:
- Pinecone vector DB populated (1,241 chunks from 28 PDFs)
- `docs/sample_questions.json` - Test questions
- `docs/sample_answers.json` - Expected answers

### 3. Launch Notebook
```bash
jupyter notebook rag_optimization_benchmark.ipynb
```

### 4. Customize Configurations
Edit the `CONFIGS_TO_TEST` list to test specific combinations:

```python
CONFIGS_TO_TEST = [
    # (embedding, retrieval, llm, prompt)
    ('bge-large-en', 'vanilla_k3', 'Llama-4-Maverick', 'baseline'),
    ('bge-large-en', 'reranked_k3', 'GPT-5-mini', 'citation_focused'),
    # Add your combinations...
]
```

### 5. Run All Cells
- Takes 15-30 minutes for ~10 configs on 5 questions
- Progress shown in real-time

## What You Get

### Outputs:
1. **rag_optimization_results.png** - 6 comprehensive charts:
   - Top 10 configurations ranking
   - Embedding model impact
   - Retrieval strategy impact
   - LLM model impact
   - Prompting strategy impact
   - Best config score breakdown

2. **CSV Files**:
   - `rag_optimization_detailed.csv` - Every test result
   - `rag_optimization_summary.csv` - Config rankings
   - `rag_component_impacts.csv` - Component analysis

3. **Console Analysis**:
   - Configuration rankings
   - Component impact breakdown
   - Optimal configuration recommendation
   - Implementation checklist

## Example Results

```
🏆 OPTIMAL RAG CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

✅ Best Configuration: bge-large-en_reranked_k3_GPT-5-mini_citation_focused

📊 Performance:
   LLM Judge Score: 87.3%
   Accuracy: 89.5%
   Citation Quality: 91.2%
   Completeness: 81.1%
   Avg Response Time: 3.2s

⚙️ Components:
   Embedding Model: bge-large-en → BAAI/bge-large-en-v1.5
   Retrieval Strategy: reranked_k3 → Two-stage rerank
   LLM Model: GPT-5-mini
   Prompting Strategy: citation_focused

💡 Key Findings:
   1. Best Embedding: bge-large-en (85.2%)
   2. Best Retrieval: reranked_k3 (86.7%)
   3. Best LLM: GPT-5-mini (88.1%)
   4. Best Prompt: citation_focused (87.9%)

🎯 Hackathon Impact:
   LLM Quality = 30% of total score
   Your score: 87.3% × 30% = 26.19 points (out of 30 max!)

📈 Improvement vs Baseline:
   +12.4% quality improvement
   = +3.72 hackathon points

═══════════════════════════════════════════════════════════════════════════════
```

## Understanding the Results

### Component Impact
The notebook analyzes each component independently:

#### Embedding Models
Shows which embedding model retrieves most relevant documents.
- **Impact**: Medium (±5% on final score)
- **Recommendation**: Use `bge-large-en` or `multilingual-e5-large`

#### Retrieval Strategies
Shows which retrieval method gets best documents.
- **Impact**: High (±10% on final score)
- **Recommendation**: `reranked_k3` usually best, `mmr_balanced` for diversity

#### LLM Models
Shows which model generates best answers.
- **Impact**: Very High (±15% on final score)
- **Recommendation**: GPT-5-mini (fast + quality) or Claude (best quality)

#### Prompting Strategies
Shows which prompt style scores highest.
- **Impact**: High (±8% on final score)
- **Recommendation**: `citation_focused` for LLM Judge

### Trade-offs

**Quality vs Speed:**
- High Quality: `reranked_k3` + `GPT-5` + `citation_focused`
- Fast: `vanilla_k3` + `GPT-5-mini` + `baseline`

**Open-Source vs Closed:**
- Open-source LLM (Llama): +20% architecture score potential
- Closed LLM (GPT/Claude): Better quality
- Analyze trade-off: If Llama is only 5% worse, use it!

## Advanced Optimization

### Test More Retrieval Parameters

```python
# In retrieval strategies section:
'vanilla_k7': {'func': retrieve_vanilla, 'params': {'top_k': 7}},
'threshold_0.75': {'func': retrieve_with_threshold, 'params': {'top_k': 10, 'threshold': 0.75}},
```

### Test Different Temperatures

```python
# Modify generate_answer call:
answer, time = generate_answer(llm_key, query, documents, prompt_key, temperature=0.1)
```

### Add Custom Prompts

```python
PROMPTING_STRATEGIES['custom'] = """
Your custom prompt here with {context} and {query}
"""
```

### Test Hybrid Search

Combine vector search with keyword search (BM25):
```python
def retrieve_hybrid(query, embed_model, top_k=3):
    # Vector search results
    vector_docs = retrieve_vanilla(query, embed_model, top_k=10)

    # BM25 keyword search (implement separately)
    keyword_docs = bm25_search(query, top_k=10)

    # Combine and rerank
    combined = merge_results(vector_docs, keyword_docs)
    return combined[:top_k]
```

## Troubleshooting

### Error: Dimension mismatch
- Only use embedding models with 1024 dimensions
- Your Pinecone index expects 1024-dim vectors
- Models to use: `bge-large-en`, `multilingual-e5-large`

### Error: Rate limit exceeded
- Add delays between API calls:
  ```python
  import time
  time.sleep(1)  # 1 second delay
  ```
- Test fewer configurations initially

### Low scores across all configs
1. Check if ground truth answers are correct
2. Verify Pinecone has relevant documents
3. Test retrieval separately to ensure docs are relevant
4. Try simpler questions first

### Out of memory
- Test fewer models at once
- Reduce `fetch_k` in reranking (from 20 to 10)
- Don't load all embedding models simultaneously

## Implementation Guide

After finding optimal config:

### 1. Update Embedding Model
```python
from sentence_transformers import SentenceTransformer

# If different from current
embed_model = SentenceTransformer('intfloat/multilingual-e5-large')
```

### 2. Implement Best Retrieval Strategy
If best is `reranked_k3`:
```python
from sentence_transformers import CrossEncoder

def retrieve_for_llm(query):
    # Stage 1: Vector search
    embedding = embed_model.encode(query)
    candidates = index.query(vector=embedding, top_k=20, include_metadata=True)

    # Stage 2: Rerank
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    pairs = [[query, doc['metadata']['text']] for doc in candidates['matches']]
    scores = reranker.predict(pairs)

    # Sort and return top 3
    ranked = sorted(zip(candidates['matches'], scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in ranked[:3]]
```

### 3. Use Best LLM and Prompt
In your `/llm` endpoint:
```python
# Use winner LLM
LLM_MODEL = "gpt-5-mini"  # Or whatever won

# Use winner prompt
SYSTEM_PROMPT = PROMPTING_STRATEGIES['citation_focused']

# Generate
response = azure_client.chat.completions.create(
    model=LLM_MODEL,
    messages=[{"role": "user", "content": SYSTEM_PROMPT.format(context=context, query=query)}],
    temperature=0.2,
    max_tokens=1000
)
```

## Next Steps

1. **Run benchmark** with default configs
2. **Analyze results** - which components matter most?
3. **Test variations** - try different combinations of top performers
4. **Implement winner** - update your main code with optimal config
5. **Validate** - test on more questions to confirm improvement

## Files Structure

```
SOCAR_Hackathon/
├── rag_optimization_benchmark.ipynb     # Main benchmark notebook
├── requirements_rag_optimization.txt    # Dependencies
├── RAG_OPTIMIZATION_README.md           # This file
├── docs/
│   ├── sample_questions.json            # Test questions
│   └── sample_answers.json              # Expected answers
└── (outputs):
    ├── rag_optimization_results.png
    ├── rag_optimization_detailed.csv
    ├── rag_optimization_summary.csv
    └── rag_component_impacts.csv
```

---

**Get the BEST RAG configuration for maximum LLM Judge score! 🚀**

This systematic approach will optimize your entire pipeline and could gain you **5-10+ hackathon points** from the LLM quality metric alone.
