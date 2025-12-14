// Show OCR Demo
function showOCRDemo() {
    const demoSection = document.getElementById('demoSection');
    const demoTitle = document.getElementById('demoTitle');
    const ocrDemo = document.getElementById('ocrDemo');
    const llmDemo = document.getElementById('llmDemo');

    demoTitle.textContent = 'OCR Demo - Extract Text from PDF';
    demoSection.style.display = 'block';
    ocrDemo.style.display = 'block';
    llmDemo.style.display = 'none';

    // Clear previous results
    document.getElementById('ocrResult').innerHTML = '';
    document.getElementById('ocrFile').value = '';

    // Smooth scroll to demo
    demoSection.scrollIntoView({ behavior: 'smooth' });
}

// Show LLM Demo
function showLLMDemo() {
    const demoSection = document.getElementById('demoSection');
    const demoTitle = document.getElementById('demoTitle');
    const ocrDemo = document.getElementById('ocrDemo');
    const llmDemo = document.getElementById('llmDemo');

    demoTitle.textContent = 'LLM Demo - Ask Questions';
    demoSection.style.display = 'block';
    ocrDemo.style.display = 'none';
    llmDemo.style.display = 'block';

    // Clear chat
    document.getElementById('chatMessages').innerHTML = '<div class="message bot-message">Hello! I can answer questions about the 28 historical SOCAR documents. What would you like to know?</div>';
    document.getElementById('questionInput').value = '';

    // Smooth scroll to demo
    demoSection.scrollIntoView({ behavior: 'smooth' });
}

// Close Demo
function closeDemo() {
    document.getElementById('demoSection').style.display = 'none';
}

// Handle OCR File Upload
async function handleOCRUpload() {
    const fileInput = document.getElementById('ocrFile');
    const resultArea = document.getElementById('ocrResult');

    if (!fileInput.files || fileInput.files.length === 0) {
        return;
    }

    const file = fileInput.files[0];

    // Validate file
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        resultArea.innerHTML = '<div class="error">Please upload a PDF file.</div>';
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        resultArea.innerHTML = '<div class="error">File size must be less than 10MB.</div>';
        return;
    }

    // Show loading
    resultArea.innerHTML = '<div class="loading">Processing PDF with Llama-4-Maverick VLM</div>';

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/ocr', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Display results
        let html = '<div class="success">OCR Completed Successfully!</div>';
        html += '<h4>Extracted Text by Page:</h4>';

        data.forEach((page, index) => {
            html += `
                <div style="margin: 20px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid var(--primary-color); border-radius: 5px;">
                    <h5 style="color: var(--primary-color); margin-bottom: 10px;">Page ${page.page_number}</h5>
                    <div style="white-space: pre-wrap; font-family: 'Courier New', monospace; line-height: 1.6;">
                        ${escapeHtml(page.MD_text)}
                    </div>
                </div>
            `;
        });

        resultArea.innerHTML = html;

    } catch (error) {
        resultArea.innerHTML = `<div class="error">Error processing PDF: ${error.message}</div>`;
        console.error('OCR Error:', error);
    }
}

// Ask Question (LLM)
async function askQuestion() {
    const questionInput = document.getElementById('questionInput');
    const chatMessages = document.getElementById('chatMessages');
    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    // Add user message
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user-message';
    userMessageDiv.textContent = question;
    chatMessages.appendChild(userMessageDiv);

    // Clear input
    questionInput.value = '';

    // Show loading
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message loading';
    loadingDiv.textContent = 'Searching documents and generating answer';
    chatMessages.appendChild(loadingDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('/llm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Remove loading
        chatMessages.removeChild(loadingDiv);

        // Add bot response
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'message bot-message';

        let responseHtml = `<div style="margin-bottom: 10px;">${escapeHtml(data.answer)}</div>`;

        if (data.sources && data.sources.length > 0) {
            responseHtml += '<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">';
            responseHtml += '<strong style="color: var(--primary-color);">Sources:</strong><ul style="margin-top: 10px; padding-left: 20px;">';
            data.sources.forEach(source => {
                responseHtml += `<li style="margin: 5px 0;"><em>${source.pdf_name}</em> - Page ${source.page_number}</li>`;
            });
            responseHtml += '</ul></div>';
        }

        botMessageDiv.innerHTML = responseHtml;
        chatMessages.appendChild(botMessageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
        // Remove loading
        chatMessages.removeChild(loadingDiv);

        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message bot-message';
        errorDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        chatMessages.appendChild(errorDiv);

        console.error('LLM Error:', error);
    }
}

// Handle Enter key in question input
document.addEventListener('DOMContentLoaded', function() {
    const questionInput = document.getElementById('questionInput');
    if (questionInput) {
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                askQuestion();
            }
        });
    }
});

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
