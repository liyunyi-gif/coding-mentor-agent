// Chat panel logic
let codeEditor = null;

function initCodeEditor() {
    const textarea = document.getElementById('code-editor');
    if (textarea && !codeEditor) {
        codeEditor = CodeMirror.fromTextArea(textarea, {
            mode: 'python',
            theme: 'monokai',
            lineNumbers: true,
            indentUnit: 4,
            tabSize: 4,
            lineWrapping: true,
        });
        codeEditor.setSize(null, 120);
    }
}

function getEditorCode() {
    return codeEditor ? codeEditor.getValue() : '';
}

function setEditorCode(code) {
    if (codeEditor) codeEditor.setValue(code);
}

function addChatMessage(role, text, isError = false) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `chat-message ${role}${isError ? ' error' : ''}`;

    // Render markdown for assistant messages
    if (role === 'assistant' && !isError) {
        div.innerHTML = `<div class="markdown-body">${marked.parse(text)}</div>`;
    } else {
        div.textContent = text;
    }

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    const code = getEditorCode();
    const sendBtn = document.getElementById('send-btn');

    if (!message && !code) return;

    const sessionId = await getOrCreateSession();
    sendBtn.disabled = true;

    // Show user message
    const displayText = code ? `${message}\n\n\`\`\`python\n${code}\n\`\`\`` : message;
    addChatMessage('user', displayText);

    input.value = '';

    try {
        const body = { message: message || '请看这段代码', session_id: sessionId };
        if (code) body.code = code;

        const data = await apiCall(`/api/sessions/${sessionId}/messages`, {
            method: 'POST',
            body: JSON.stringify(body),
            timeout: 60000, // 60s for LLM responses
        });

        if (data.assistant_message) {
            addChatMessage('assistant', data.assistant_message);
        }
    } catch (err) {
        addChatMessage('error', `错误: ${err.message}`, true);
    } finally {
        sendBtn.disabled = false;
        setEditorCode('');
    }
}

// Init chat
document.addEventListener('DOMContentLoaded', () => {
    initCodeEditor();

    document.getElementById('send-btn').addEventListener('click', sendMessage);
    document.getElementById('chat-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});
