let currentData = null;

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById('filename').innerText = file.name;
        document.getElementById('file-info').classList.remove('hidden');
        document.getElementById('uploadBtn').classList.remove('hidden');
    }
}

async function startPipeline() {
    const fileInput = document.getElementById('pdfInput');
    const btn = document.getElementById('uploadBtn');

    if (!fileInput.files[0]) return;

    btn.disabled = true;
    btn.innerText = "Processing...";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch('/api/process', { method: 'POST', body: formData });
        currentData = await response.json();

        document.getElementById('jsonOutput').innerText = JSON.stringify(currentData.json_preview, null, 2);

        const grid = document.getElementById('chunksOutput');
        grid.innerHTML = '';
        currentData.chunks_preview.forEach(chunk => {
            const card = document.createElement('div');
            card.className = 'chunk-card';
            card.innerHTML = `
                <div class="chunk-meta">Page ${chunk.metadata.page} • ${chunk.text.length} chars</div>
                <div class="chunk-text">${chunk.text}</div>
            `;
            grid.appendChild(card);
        });

        nextPage(2);

    } catch (error) {
        alert("Error: " + error.message);
        btn.disabled = false;
        btn.innerText = "Try Again";
    }
}

function nextPage(pageNumber) {
    document.querySelectorAll('.page').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));

    document.getElementById(`page-${pageNumber}`).classList.remove('hidden');
    document.getElementById(`page-${pageNumber}`).classList.add('active');

    document.querySelectorAll('.step').forEach(el => el.classList.remove('active'));
    document.getElementById(`step${pageNumber}`).classList.add('active');
}

async function askGemini() {
    const input = document.getElementById('userQuestion');
    const question = input.value.trim();
    if (!question) return;

    addMessage("You", question, "user");
    input.value = '';

    const loadingId = addMessage("Gemini", "...", "ai");

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        const data = await response.json();

        const htmlAnswer = marked.parse(data.answer);
        updateMessage(loadingId, htmlAnswer);

    } catch (error) {
        updateMessage(loadingId, "Error getting response.");
    }
}

function addMessage(name, text, type) {
    const history = document.getElementById('chatHistory');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.id = 'msg-' + Date.now();
    msgDiv.innerHTML = `<div class="bubble">${text}</div>`;
    history.appendChild(msgDiv);
    history.scrollTop = history.scrollHeight;
    return msgDiv.id;
}

function updateMessage(id, html) {
    const bubble = document.querySelector(`#${id} .bubble`);
    if (bubble) bubble.innerHTML = html;
}

function handleEnter(e) {
    if (e.key === 'Enter') askGemini();
}