// Main app controller — tab switching and initialization
document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.panel');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;

            // Update active tab
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Show panel
            panels.forEach(p => p.classList.remove('active'));
            const panel = document.getElementById(`${tabName}-panel`);
            if (panel) panel.classList.add('active');

            // Refresh panel data on switch
            if (tabName === 'progress') {
                loadProgress();
            } else if (tabName === 'practice') {
                checkPracticeAvailability();
            }
        });
    });

    // Initialize session on load
    getOrCreateSession().catch(err => {
        console.error('Failed to create session:', err);
        document.getElementById('session-id-display').textContent = '连接失败';
    });
});
