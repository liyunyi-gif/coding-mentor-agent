// Progress panel logic
async function loadProgress() {
    try {
        const data = await apiCall('/api/progress/me');

        // Profile info
        document.getElementById('profile-info').innerHTML = `
            <p>当前水平: <strong>${data.current_level}</strong></p>
            <p>整体进度: <strong>${data.course_progress_percent}%</strong></p>
            <p>诊断状态: <strong>${statusLabel(data.diagnostic_state)}</strong></p>
            <p>练习状态: <strong>${practiceLabel(data.practice_state)}</strong></p>
        `;

        // Mastery list
        const masteryList = document.getElementById('mastery-list');
        if (data.mastery && data.mastery.length > 0) {
            masteryList.innerHTML = data.mastery.map(m => `
                <div class="mastery-item">
                    <span>${m.name || m.concept_id}</span>
                    <div class="mastery-bar">
                        <div class="mastery-fill ${levelClass(m.mastery_level)}" style="width:${m.mastery_level}%"></div>
                    </div>
                    <span style="font-size:12px;color:#888;min-width:45px;">${m.mastery_level}%</span>
                </div>
            `).join('');
        } else {
            masteryList.innerHTML = '<p style="color:#888;">暂无掌握度数据</p>';
        }

        // Weak concepts
        const weakList = document.getElementById('weak-list');
        if (data.weak_concepts && data.weak_concepts.length > 0) {
            weakList.innerHTML = data.weak_concepts.map(w => `
                <div class="mastery-item">
                    <span>${w.name}</span>
                    <span class="badge weak">${w.reason}</span>
                </div>
            `).join('');
        } else if (data.mastery && data.mastery.length > 0) {
            weakList.innerHTML = '<p style="color:#4caf50;">所有概念掌握良好 ✓</p>';
        } else {
            weakList.innerHTML = '<p style="color:#888;">请先完成诊断</p>';
        }

        // Curriculum
        const curriculumDiv = document.getElementById('curriculum-progress');
        if (data.curriculum && data.curriculum.length > 0) {
            curriculumDiv.innerHTML = data.curriculum.map(c => `
                <div class="mastery-item">
                    <span>${c.title}</span>
                    <span class="badge ${c.status === 'completed' ? 'stable' : c.status === 'current' ? '' : ''}">${c.status === 'completed' ? '已完成' : c.status === 'current' ? '进行中' : '待学'}</span>
                </div>
            `).join('');
        } else {
            curriculumDiv.innerHTML = '<p style="color:#888;">暂无课程数据</p>';
        }
    } catch (err) {
        document.getElementById('progress-content').innerHTML =
            `<p style="color:#f44336;">加载进度失败: ${err.message}</p>`;
    }
}

function statusLabel(state) {
    const labels = {
        'not_started': '未开始',
        'active': '进行中',
        'completed': '已完成',
    };
    return labels[state] || state;
}

function practiceLabel(state) {
    const labels = {
        'locked_by_diagnostic': '需先完成诊断',
        'available_after_explicit_request': '可请求练习',
    };
    return labels[state] || state;
}

function levelClass(level) {
    if (level >= 80) return 'high';
    if (level >= 50) return 'medium';
    return 'low';
}

// Init progress
document.addEventListener('DOMContentLoaded', () => {
    loadProgress();
});
