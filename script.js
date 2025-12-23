let selectedFile = null;

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    selectedFile = file;


    document.getElementById('filename-display').textContent = file.name;


    const parseBtn = document.getElementById('parseBtn');
    if (parseBtn) parseBtn.disabled = false;

   
    const tokenBtn = document.getElementById('tokenBtn');
    if (tokenBtn) {
        tokenBtn.style.display = 'none';
        tokenBtn.disabled = true;
    }


    const fileURL = URL.createObjectURL(file);
    const iframe = document.getElementById('pdfFrame');
    const placeholder = document.getElementById('pdfPlaceholder');

    if (iframe && placeholder) {
        iframe.src = fileURL;
        iframe.style.display = 'block';
        placeholder.style.display = 'none';
    }


    document.getElementById('jsonOutput').innerHTML = '';
    document.getElementById('statusText').textContent = 'Ready to parse';
}

async function uploadPDF(mode = 'parse') {
    if (!selectedFile) return;

    const parseBtn = document.getElementById('parseBtn');
    const tokenBtn = document.getElementById('tokenBtn');
    const loader = document.getElementById('loader');
    const output = document.getElementById('jsonOutput');
    const status = document.getElementById('statusText');


    if (parseBtn) parseBtn.disabled = true;
    if (tokenBtn) tokenBtn.disabled = true;

    loader.style.display = 'flex';

    const formData = new FormData();
    formData.append("file", selectedFile);

    const endpoint = mode === 'tokenize' ? '/api/tokenize' : '/api/parse';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(response.statusText);

        const data = await response.json();

        output.innerHTML = syntaxHighlight(data);

        if (mode === 'tokenize') {
            status.textContent = `✓ Created ${data.total_chunks || 0} Chunks`;
            status.style.color = "#4ade80";
        } else {
            status.textContent = `✓ Processed ${data.total_pages || 0} Pages`;
            status.style.color = "#4ade80";

            if (tokenBtn) {
                tokenBtn.style.display = 'inline-flex'; 
                tokenBtn.disabled = false;              
            }
        }

    } catch (error) {
        output.textContent = "Error: " + error.message;
        output.style.color = "#ff6b6b";
        status.textContent = "Failed";
        status.style.color = "#ff6b6b";
    } finally {
        
        if (parseBtn) parseBtn.disabled = false;
        if (tokenBtn && tokenBtn.style.display !== 'none') tokenBtn.disabled = false;
        loader.style.display = 'none';
    }
}

function syntaxHighlight(json) {
    if (typeof json != 'string') json = JSON.stringify(json, undefined, 2);
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        let cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) cls = 'key';
            else cls = 'string';
        } else if (/true|false/.test(match)) cls = 'boolean';
        else if (/null/.test(match)) cls = 'null';
        return '<span class="' + cls + '">' + match + '</span>';
    });
}