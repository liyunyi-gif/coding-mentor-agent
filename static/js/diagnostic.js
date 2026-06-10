// Diagnostic panel logic
let currentDiagnosticId = null;
let currentQuestionData = null;

async function startDiagnostic() {
    const sessionId = await getOrCreateSession();
    const area = document.getElementById('diagnostic-area');
    const btn = document.getElementById('start-diagnostic-btn');

    btn.disabled = true;
    btn.textContent = '加载中...';

    try {
        const data = await apiCall(`/api/diagnostics/next?session_id=${sessionId}`);

        if (data.completed) {
            area.innerHTML = `
                <div class="feedback-area success">
                    <p>诊断测评已完成！共回答了 ${data.total_answered} 题。</p>
                    <p>你现在可以开始练习了。</p>
                </div>`;
            btn.style.display = 'none';
            return;
        }

        currentDiagnosticId = data.diagnostic_id;
        currentQuestionData = data;
        renderQuestion(data);
        btn.textContent = '下一题';
    } catch (err) {
        area.innerHTML = `<div class="feedback-area fail">加载诊断题失败: ${err.message}</div>`;
        btn.textContent = '重试';
    } finally {
        btn.disabled = false;
    }
}

function renderQuestion(data) {
    const area = document.getElementById('diagnostic-area');
    const feedback = document.getElementById('diagnostic-feedback');
    feedback.innerHTML = '';

    const questionNum = data.total_answered + 1;
    let html = `
        <div class="question-card">
            <h3>第 ${questionNum} 题 — ${data.concept_name}</h3>
            <p style="margin-bottom:12px;font-size:15px;">${data.question}</p>
            <div id="options-container">
    `;

    data.options.forEach((opt, idx) => {
        html += `
            <button class="option-btn" data-index="${idx}" onclick="selectOption(${idx})">
                ${String.fromCharCode(65 + idx)}. ${opt}
            </button>
        `;
    });

    html += '</div></div>';
    area.innerHTML = html;
}

async function selectOption(index) {
    if (!currentDiagnosticId || !currentQuestionData) return;

    // Disable all options
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.disabled = true;
        btn.style.pointerEvents = 'none';
    });

    try {
        const data = await apiCall(`/api/diagnostics/${currentDiagnosticId}/answers`, {
            method: 'POST',
            body: JSON.stringify({
                answer_index: index,
                concept_id: currentQuestionData.concept_id,
                question: currentQuestionData.question,
                difficulty: currentQuestionData.difficulty,
            }),
        });

        // Show feedback
        const feedback = document.getElementById('diagnostic-feedback');
        const selectedBtn = document.querySelector(`[data-index="${index}"]`);

        if (data.correct) {
            selectedBtn.classList.add('correct');
            feedback.className = 'feedback-area success';
            feedback.textContent = '✓ 正确！';
        } else {
            selectedBtn.classList.add('wrong');
            feedback.className = 'feedback-area fail';
            feedback.textContent = '✗ 继续加油！';
        }

        // Update start button to "next"
        const btn = document.getElementById('start-diagnostic-btn');
        btn.textContent = '下一题';
        btn.style.display = '';

    } catch (err) {
        const feedback = document.getElementById('diagnostic-feedback');
        feedback.className = 'feedback-area fail';
        feedback.textContent = `提交失败: ${err.message}`;
    }
}

// Init diagnostic
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('start-diagnostic-btn').addEventListener('click', startDiagnostic);
});
