const API_BASE = 'http://127.0.0.1:8000/api';

// Theme Toggle Logic
const themeToggle = document.getElementById('theme-toggle');
const htmlEl = document.documentElement;

// Set initial theme based on system preference or default to dark
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    htmlEl.setAttribute('data-theme', 'light');
}

themeToggle.addEventListener('click', () => {
    const currentTheme = htmlEl.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    htmlEl.setAttribute('data-theme', newTheme);
});

// Tab Navigation Logic
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));

        // Add active class to clicked
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});

// Loader controls
const showLoader = () => document.getElementById('loader').classList.remove('hidden');
const hideLoader = () => document.getElementById('loader').classList.add('hidden');

// --- Feature 1: Top Candidates ---
async function fetchCandidates() {
    showLoader();
    try {
        const res = await fetch(`${API_BASE}/top-candidates`);
        if (!res.ok) throw new Error('Failed to fetch candidates');
        
        const data = await res.json();
        renderCandidates(data.candidates);
    } catch (err) {
        alert(err.message);
    } finally {
        hideLoader();
    }
}

function renderCandidates(candidates) {
    const container = document.getElementById('candidates-container');
    container.innerHTML = ''; // clear existing

    candidates.forEach(cand => {
        const card = document.createElement('div');
        card.className = 'glass-panel candidate-card';
        
        const skillsHtml = (cand.skills || []).slice(0, 5).map(s => `<span class="skill-tag">${s}</span>`).join('');
        
        card.innerHTML = `
            <div class="card-header">
                <div>
                    <div class="candidate-name">${cand.profile?.anonymized_name || 'Unknown Candidate'}</div>
                    <div class="candidate-title">${cand.profile?.current_title || 'Unknown Title'} @ ${cand.profile?.current_company || 'Unknown Company'} | ${cand.profile?.years_of_experience || 'N/A'} YOE</div>
                </div>
                <div class="rank-badge">Rank #${cand.rank}</div>
            </div>
            
            <div class="score-container">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%" data-target="${cand.score * 100}%"></div>
                </div>
                <div class="score-text">${cand.score.toFixed(4)}</div>
            </div>
            
            <div class="skills-list">
                ${skillsHtml}
                ${cand.skills && cand.skills.length > 5 ? `<span class="skill-tag">+${cand.skills.length - 5} more</span>` : ''}
            </div>
            
            <div class="reasoning">
                <strong>Reasoning:</strong> ${cand.reasoning}
            </div>
        `;
        
        container.appendChild(card);
    });

    // Trigger progress bar animations after a slight delay
    setTimeout(() => {
        document.querySelectorAll('.progress-fill').forEach(bar => {
            bar.style.width = bar.getAttribute('data-target');
        });
    }, 100);
}

// --- Feature 2: Talent Memory ---
async function searchMemory() {
    const query = document.getElementById('memory-query').value.trim();
    if (!query) return alert('Please enter a query');

    showLoader();
    try {
        const res = await fetch(`${API_BASE}/memory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        if (!res.ok) throw new Error('Failed to query memory');
        const data = await res.json();
        renderMemoryResults(data.results);
    } catch (err) {
        alert(err.message);
    } finally {
        hideLoader();
    }
}

function renderMemoryResults(results) {
    const container = document.getElementById('memory-results');
    
    if (!results || results.length === 0) {
        container.innerHTML = '<div class="glass-panel" style="padding: 2rem; text-align: center;">No results found.</div>';
        return;
    }

    let html = `
        <div class="glass-panel" style="overflow-x: auto;">
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Candidate ID</th>
                        <th>Name</th>
                        <th>Title</th>
                        <th>Distance (Lower = Better)</th>
                    </tr>
                </thead>
                <tbody>
    `;

    results.forEach(r => {
        html += `
            <tr>
                <td><code>${r.candidate_id}</code></td>
                <td><strong>${r.name}</strong></td>
                <td>${r.title}</td>
                <td>${r.distance.toFixed(4)}</td>
            </tr>
        `;
    });

    html += `</tbody></table></div>`;
    container.innerHTML = html;
}

// --- Feature 3: Gap Analysis ---
async function fetchGapAnalysis() {
    showLoader();
    try {
        const res = await fetch(`${API_BASE}/gap-analysis`);
        if (!res.ok) throw new Error('Failed to fetch gap analysis');
        
        const data = await res.json();
        const container = document.getElementById('gap-report');
        
        // Parse markdown using marked.js
        container.innerHTML = marked.parse(data.report);
    } catch (err) {
        alert(err.message);
    } finally {
        hideLoader();
    }
}
