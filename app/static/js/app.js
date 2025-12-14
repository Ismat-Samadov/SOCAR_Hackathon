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

    // Show animated loading
    resultArea.innerHTML = `
        <div class="loading-animated">
            <div class="loading-spinner"></div>
            <div class="loading-status">Preparing PDF for processing...</div>
            <div class="loading-progress">
                <div class="progress-bar"></div>
            </div>
            <div class="ocr-stats">
                <div class="stat-item">
                    <span class="stat-icon">📄</span>
                    <span class="stat-label">Model: Llama-4-Maverick-17B</span>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">🎯</span>
                    <span class="stat-label">Accuracy: 88.3% CSR</span>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">🌍</span>
                    <span class="stat-label">Languages: AZ, RU, EN</span>
                </div>
            </div>
        </div>
    `;

    // Animated OCR status updates
    const ocrStatuses = [
        '📄 Converting PDF to images...',
        '🔍 Analyzing document layout...',
        '🤖 Running Vision-Language Model...',
        '📝 Extracting text with 88.3% accuracy...',
        '🔤 Preserving Cyrillic and Latin characters...',
        '🖼️ Detecting embedded images...',
        '✨ Finalizing OCR results...'
    ];

    let ocrStatusIndex = 0;
    const statusElement = resultArea.querySelector('.loading-status');
    const progressBar = resultArea.querySelector('.progress-bar');

    const ocrStatusInterval = setInterval(() => {
        if (ocrStatusIndex < ocrStatuses.length) {
            statusElement.textContent = ocrStatuses[ocrStatusIndex];
            progressBar.style.width = `${((ocrStatusIndex + 1) / ocrStatuses.length) * 100}%`;
            ocrStatusIndex++;
        }
    }, 1500);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/ocr', {
            method: 'POST',
            body: formData
        });

        clearInterval(ocrStatusInterval);

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
        clearInterval(ocrStatusInterval);
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

    // Show animated loading with status updates
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message loading-animated';
    loadingDiv.innerHTML = `
        <div class="loading-spinner"></div>
        <div class="loading-status">Initializing AI systems...</div>
        <div class="loading-progress">
            <div class="progress-bar"></div>
        </div>
    `;
    chatMessages.appendChild(loadingDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Animated status updates
    const statusMessages = [
        '🔍 Searching 1,128 vectors across 28 historical documents...',
        '🧠 Embedding your question with BAAI/bge-large-en-v1.5...',
        '📊 Retrieving top-3 most relevant document chunks...',
        '🤖 Generating answer with Llama-4-Maverick-17B...',
        '📝 Adding citations from source documents...',
        '✨ Finalizing response...'
    ];

    let statusIndex = 0;
    const statusElement = loadingDiv.querySelector('.loading-status');
    const progressBar = loadingDiv.querySelector('.progress-bar');

    const statusInterval = setInterval(() => {
        if (statusIndex < statusMessages.length) {
            statusElement.textContent = statusMessages[statusIndex];
            progressBar.style.width = `${((statusIndex + 1) / statusMessages.length) * 100}%`;
            statusIndex++;
        }
    }, 1200);

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

        // Clear status interval and remove loading
        clearInterval(statusInterval);
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
        // Clear status interval and remove loading
        clearInterval(statusInterval);
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
