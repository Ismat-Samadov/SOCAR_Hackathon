# Vision-Language Model (VLM) OCR Benchmarking

## Why VLMs Instead of Traditional OCR?

**Traditional OCR** (Tesseract, EasyOCR, PaddleOCR):
- ❌ Limited accuracy on handwriting
- ❌ Poor multi-language support
- ❌ No context understanding
- ❌ Struggles with complex layouts

**Vision-Language Models** (GPT-4.1, GPT-5, Claude, etc.):
- ✅ **State-of-the-art accuracy** (90%+ CSR typical)
- ✅ **Understands context** - better at ambiguous characters
- ✅ **Multi-language native** - Azerbaijani, Russian, English
- ✅ **Handles complexity** - handwriting, tables, mixed layouts
- ✅ **No separate pipeline** - directly image → text

## Available Vision Models

From your Azure deployment (screenshot):

| Model | Vision Support | Rating | Notes |
|-------|---------------|--------|-------|
| **GPT-4.1** | ✅ Yes | ⭐⭐⭐⭐⭐ | Excellent OCR capability |
| **GPT-5** | ✅ Yes | ⭐⭐⭐⭐⭐ | Latest, best performance |
| **GPT-5-mini** | ✅ Yes | ⭐⭐⭐⭐⭐ | Fast + excellent quality |
| **Claude-Sonnet-4.5** | ✅ Yes | ⭐⭐⭐⭐⭐ | Very good OCR |
| **Phi-4-multimodal** | ✅ Yes | ⭐⭐⭐⭐ | Explicitly multimodal |
| **Llama-4-Maverick** | ⚠️ Check | ⭐⭐⭐⭐ | May have vision support |

## Evaluation Metrics

### Hackathon Primary Metrics:
- **CSR** (Character Success Rate) = 100 - CER
  - Target: >90% for excellent score
  - This is 50% of your total hackathon score!

- **WSR** (Word Success Rate) = 100 - WER
  - Measures word-level accuracy

### Additional Metrics:
- **CER** (Character Error Rate) - Lower is better
- **WER** (Word Error Rate) - Lower is better
- **Response Time** - Processing speed
- **Length Accuracy** - How complete the extraction is

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements_vlm_ocr.txt
```

### 2. Ensure Ground Truth Exists
You need:
- `data/pdfs/document_00.pdf` - Test PDF
- `data/document_00.md` - Ground truth text

### 3. Launch Notebook
```bash
jupyter notebook vlm_ocr_benchmark.ipynb
```

### 4. Run All Cells
- **Cell → Run All**
- Takes ~5-10 minutes (depends on # of pages and models)
- Progress shown in real-time

## What Happens

### For Each VLM:
1. **Convert PDF to images** (150 DPI for quality)
2. **Send to vision model** with optimized OCR prompt
3. **Extract text** page by page
4. **Calculate metrics** vs ground truth
5. **Generate visualizations** and rankings

### OCR Prompt Used:
```
You are an expert OCR system for historical oil & gas documents.

Extract ALL text with 100% accuracy:
1. Preserve EXACT spelling (Azerbaijani, Russian, English)
2. Maintain original Cyrillic - DO NOT transliterate
3. Keep all numbers, symbols exactly as shown
4. Preserve layout structure
5. Include ALL text - headers, body, footnotes, tables
6. If unclear, make best effort but stay accurate

Output ONLY extracted text. No explanations.
```

## Expected Results

### Typical Performance:
- **GPT-5/Claude**: 92-96% CSR (Excellent)
- **GPT-4.1**: 88-92% CSR (Very Good)
- **Phi-4**: 85-90% CSR (Good)

### Time:
- ~10-30 seconds per page
- 12-page document ≈ 2-6 minutes total

## Output Files

After running:
```
vlm_ocr_benchmark_results.png          # 4 comparison charts
vlm_ocr_benchmark_detailed.csv         # Full metrics
vlm_ocr_benchmark_rankings.csv         # Final rankings
```

### Visualization Includes:
1. **CSR Comparison** (main metric)
2. **WSR Comparison**
3. **Processing Speed**
4. **Error Rates** (CER vs WER)

## Interpreting Results

### Example Output:
```
🏆 FINAL RANKINGS
═══════════════════════════════════════════════════════════════════
Rank  Model               CSR      WSR      CER     WER    Time
1     GPT-5              94.52%   91.23%   5.48%   8.77%  145s
2     Claude-Sonnet-4.5  93.18%   89.45%   6.82%   10.55% 167s
3     GPT-4.1            91.67%   87.92%   8.33%   12.08% 152s
4     GPT-5-mini         90.34%   86.11%   9.66%   13.89% 98s
5     Phi-4-multimodal   87.21%   83.44%   12.79%  16.56% 112s
═══════════════════════════════════════════════════════════════════

💡 RECOMMENDATION: Use GPT-5
   CSR: 94.52% × 50% = 47.26 hackathon points (out of 50 max!)
   ✅ EXCELLENT - This will score very high on OCR!
```

### Scoring Impact:
- **90-100% CSR**: Excellent (45-50 points)
- **80-90% CSR**: Good (40-45 points)
- **70-80% CSR**: Fair (35-40 points)
- **<70% CSR**: Needs improvement

## Customization

### Test Fewer Models (Faster):
Edit cell:
```python
MODELS_TO_TEST = [
    'GPT-5',           # Test only this one
    # 'Claude-Sonnet-4.5',  # Comment out
]
```

### Adjust Image Quality:
Higher DPI = better OCR but slower:
```python
images = pdf_to_images(pdf_path, dpi=200)  # Default: 150
```

### Change OCR Prompt:
Modify the `system_prompt` in `vlm_extract_text()` function.

## Troubleshooting

### Error: "Model does not support vision"
- Some models may not have vision API enabled
- Remove from `MODELS_TO_TEST` list
- Check Azure deployment configuration

### Error: "Rate limit exceeded"
- VLM APIs have strict rate limits
- Add delay between pages:
  ```python
  time.sleep(2)  # 2 second delay
  ```

### Low CSR (<80%)
- Try different model (GPT-5 usually best)
- Increase image DPI (150 → 200)
- Adjust OCR prompt to emphasize Azerbaijani/Cyrillic
- Check if ground truth formatting matches

### Slow Performance
- Use faster model (GPT-5-mini)
- Reduce image DPI (150 → 100)
- Test on fewer pages first

## Next Steps

1. **Run benchmark** on `document_00.pdf`
2. **Identify best model** (highest CSR)
3. **Implement in your code**:
   - Use winner VLM in `/ocr` endpoint
   - Apply same prompt as tested
   - Convert PDF → images → VLM → text

4. **Test on more documents**:
   - Easy: Azerbaijani Latin printed
   - Medium: Cyrillic/Russian printed
   - Hard: Azerbaijani handwritten (highest points!)

## Implementation Example

After finding the best model:

```python
# In your /ocr endpoint
from openai import AzureOpenAI
import fitz  # PyMuPDF
from PIL import Image

def ocr_with_vlm(pdf_bytes: bytes) -> list:
    # Convert to images
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    results = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Convert to base64
        image_b64 = image_to_base64(image)

        # Call VLM (use winner from benchmark!)
        response = azure_client.chat.completions.create(
            model="gpt-5",  # Use your winner model
            messages=[
                {"role": "system", "content": "OCR prompt here..."},
                {"role": "user", "content": [
                    {"type": "text", "text": f"Extract text from page {page_num+1}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                ]}
            ],
            temperature=0.0
        )

        text = response.choices[0].message.content
        results.append({"page_number": page_num + 1, "MD_text": text})

    return results
```

## Files Structure

```
SOCAR_Hackathon/
├── vlm_ocr_benchmark.ipynb        # Main benchmark notebook
├── requirements_vlm_ocr.txt       # Dependencies
├── VLM_OCR_README.md              # This file
├── data/
│   ├── pdfs/document_00.pdf       # Test PDF
│   └── document_00.md             # Ground truth
└── (outputs):
    ├── vlm_ocr_benchmark_results.png
    ├── vlm_ocr_benchmark_detailed.csv
    └── vlm_ocr_benchmark_rankings.csv
```

---

**Ready to test state-of-the-art VLM OCR! 🚀**

This approach will give you **significantly better** OCR accuracy than traditional methods, especially on:
- Handwritten Azerbaijani (206.25 hackathon points!)
- Mixed Cyrillic/Latin scripts
- Complex document layouts
