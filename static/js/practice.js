// Practice panel logic
let activeContractId = null;

async function requestPractice() {
    const sessionId = await getOrCreateSession();
    const btn = document.getElementById('request-practice-btn');
    const status = document.getElementById('practice-status');

    btn.disabled = true;
    btn.textContent = '加载中...';

    try {
        const data = await apiCall(`/api/sessions/${sessionId}/practice`, {
            method: 'POST',
            body: JSON.stringify({}),
        });

        if (data.kind === 'practice_locked') {
            status.innerHTML = `<p style="color:#f44336;">${data.message}</p>`;
            status.style.display = 'block';
            btn.style.display = 'none';
            return;
        }

        if (data.kind === 'exercise_ready') {
            const ex = data.exercise;
            activeContractId = ex.practice_contract_id || ex.id;

            document.getElementById('exercise-title').textContent = ex.title;
            document.getElementById('exercise-prompt').innerHTML = marked.parse(ex.prompt_md);

            const checklist = document.getElementById('exercise-checklist');
            if (ex.acceptance_checklist && ex.acceptance_checklist.length > 0) {
                checklist.innerHTML = '<h4>验收标准</h4><ul>' +
                    ex.acceptance_checklist.map(item => `<li>${item}</li>`).join('') +
                    '</ul>';
            }

            document.getElementById('practice-exercise').style.display = 'block';
            document.getElementById('practice-status').style.display = 'none';

            status.style.display = 'block';
            status.innerHTML = `<p style="color:#4caf50;">${data.message}</p>
                <p style="color:#888;font-size:13px;">切换到聊天面板，在代码编辑器中编写代码，然后发送消息提交。</p>`;

            btn.textContent = '换一题';
        }
    } catch (err) {
        status.innerHTML = `<p style="color:#f44336;">请求练习失败: ${err.message}</p>`;
        status.style.display = 'block';
    } finally {
        btn.disabled = false;
    }
}

async function checkPracticeAvailability() {
    try {
        const data = await apiCall('/api/progress/me');
        const btn = document.getElementById('request-practice-btn');
        const status = document.getElementById('practice-status');

        if (data.practice_state === 'available_after_explicit_request') {
            btn.style.display = 'inline-block';
            status.innerHTML = '<p style="color:#4caf50;">诊断已完成，可以开始练习！</p>';
            status.style.display = 'block';
        } else if (data.diagnostic_state === 'active') {
            status.innerHTML = '<p>诊断进行中，完成诊断后可解锁练习。</p>';
            status.style.display = 'block';
            btn.style.display = 'none';
        } else {
            status.innerHTML = '<p>请先完成诊断测评。</p>';
            status.style.display = 'block';
            btn.style.display = 'none';
        }
    } catch (err) {
        console.error('Practice check failed:', err);
    }
}

// Init practice
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('request-practice-btn').addEventListener('click', requestPractice);
});
