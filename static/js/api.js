// API helper with timeout and error handling
const API_BASE = '';

async function apiCall(url, options = {}) {
    const controller = new AbortController();
    const timeoutMs = options.timeout || 30000;
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    try {
        const res = await fetch(API_BASE + url, {
            ...options,
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });
        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || errData.message || `请求失败 (${res.status})`);
        }
        return await res.json();
    } catch (err) {
        if (err.name === 'AbortError') {
            throw new Error('请求超时，请检查服务是否启动');
        }
        throw err;
    } finally {
        clearTimeout(timeout);
    }
}

// Session management
let currentSessionId = null;

async function getOrCreateSession() {
    if (currentSessionId) return currentSessionId;

    // Try resume
    try {
        const data = await apiCall('/api/sessions', {
            method: 'POST',
            body: JSON.stringify({ resume: true }),
        });
        currentSessionId = data.session_id;
        document.getElementById('session-id-display').textContent =
            `会话: ${currentSessionId.slice(0, 12)}...`;
        return currentSessionId;
    } catch {
        // Create new
        const data = await apiCall('/api/sessions', {
            method: 'POST',
            body: JSON.stringify({ resume: false }),
        });
        currentSessionId = data.session_id;
        document.getElementById('session-id-display').textContent =
            `会话: ${currentSessionId.slice(0, 12)}...`;
        return currentSessionId;
    }
}

// SSE event stream
function connectSSE(sessionId, onEvent) {
    const eventSource = new EventSource(`${API_BASE}/api/sessions/${sessionId}/events`);

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            onEvent(data);
        } catch (e) {
            console.error('SSE parse error:', e);
        }
    };

    eventSource.onerror = () => {
        console.warn('SSE connection error, will retry...');
    };

    return eventSource;
}
