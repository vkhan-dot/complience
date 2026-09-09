// Compliance Centras - SPA Controller

function getSvgIcon(name, size = 15) {
    const icons = {
        'dashboard': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9" rx="1"></rect><rect x="14" y="3" width="7" height="5" rx="1"></rect><rect x="14" y="12" width="7" height="9" rx="1"></rect><rect x="3" y="16" width="7" height="5" rx="1"></rect></svg>`,
        'search': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
        'tasks': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"></path><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"></path><path d="M7 21h10"></path><path d="M12 3v18"></path><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"></path></svg>`,
        'documents': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>`,
        'relations': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>`,
        'prompts': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line><line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line><line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line></svg>`,
        'chat': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`,
        'sandbox': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v7.31"></path><path d="M14 2v7.31"></path><path d="M8.5 2h7"></path><path d="M14 9.3a6.5 6.5 0 1 1-4 0"></path><path d="M5.52 16h12.96"></path></svg>`,
        'plus': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,
        'upload': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>`,
        'refresh': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>`,
        'telegram': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`,
        'trash': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`,
        'check': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
        'edit': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>`,
        'file': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>`,
        'building': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><line x1="9" y1="22" x2="9" y2="22"></line><line x1="9" y1="18" x2="9" y2="18"></line><line x1="9" y1="14" x2="9" y2="14"></line><line x1="9" y1="10" x2="9" y2="10"></line><line x1="9" y1="6" x2="9" y2="6"></line><line x1="15" y1="22" x2="15" y2="22"></line><line x1="15" y1="18" x2="15" y2="18"></line><line x1="15" y1="14" x2="15" y2="14"></line><line x1="15" y1="10" x2="15" y2="10"></line><line x1="15" y1="6" x2="15" y2="6"></line></svg>`
    };
    return icons[name] || '';
}

let activeTab = 'dashboard';
let activeTaskId = null;
let activeDraftTab = 'rules';
let activePromptKey = null;
let currentTaskData = null;
let editingSourceId = null;
let editingSourceIsActive = true;

document.addEventListener('DOMContentLoaded', () => {
    if (checkAuth()) {
        loadDashboard();
        checkNotifications();
    }
    setInterval(() => {
        if (localStorage.getItem('token')) {
            checkNotifications();
        }
    }, 20000);
    
    // Global Keyboard Shortcuts (Ctrl+K for Command Palette, Esc for Modals/Drawers)
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            openCommandPalette();
        } else if (e.key === 'Escape') {
            closeCommandPalette();
            closeDrawer();
        }
    });

    // Auth Form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleLogin();
        });
    }

    // Nav menu routing
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = item.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Check URL hash on load
    if (localStorage.getItem('token')) {
        if (window.location.hash) {
            const tab = window.location.hash.substring(1);
            switchTab(tab);
        } else {
            switchTab('monitoring');
        }
    }
});

function switchTab(tabName) {
    activeTab = tabName;
    window.location.hash = tabName;
    
    // Update active nav class
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        if (item.getAttribute('data-tab') === tabName) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Show active screen
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => {
        if (screen.id === tabName) {
            screen.classList.add('active');
        } else {
            screen.classList.remove('active');
        }
    });

    // Update header page title & subtitle
    const headings = {
        'monitoring': 'Мониторинг нормативно-правовых актов',
        'tasks': 'Сравнение редакций и инспектор изменений',
        'sandbox': 'Быстрое сравнение документов и ссылок',
        'documents': 'Внутренние регламенты и стандарты компании'
    };
    const subtitles = {
        'monitoring': 'Отслеживание обновлений в законодательстве РК (Параграф, Әділет, Zakon) и локальных актах',
        'tasks': 'Постатейный визуальный Side-by-Side инспектор правок, сравнительные таблицы и пакеты изменений',
        'sandbox': 'Сравнение любых 2 файлов или веб-ссылок в 1 клик без добавления на постоянный мониторинг',
        'documents': 'Внутренние правила страхования, методологические инструкции и договоры компании'
    };
    const headEl = document.getElementById('page-title-heading');
    if (headEl) headEl.innerText = headings[tabName] || 'Мониторинг законодательства';
    const subEl = document.getElementById('page-subtitle-text');
    if (subEl) subEl.innerText = subtitles[tabName] || '';

    // Load tab content

    if (tabName === 'dashboard') { loadDashboard(); checkNotifications(); }
    else if (tabName === 'monitoring') { loadMonitoring(); loadSchedulerStatus(); }
    else if (tabName === 'tasks') showTasksList();
    else if (tabName === 'documents') loadInternalDocs();
    else if (tabName === 'relations') drawRelationsGraph();
    else if (tabName === 'prompts') loadPromptsZone();
    else if (tabName === 'sandbox') initSandboxListeners();
}



// ----------------- UI Helpers (Toasts) -----------------
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-out forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

// ----------------- API GET / POST Helpers -----------------

function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('app-container').style.display = 'flex';
        return true;
    } else {
        document.getElementById('login-screen').style.display = 'flex';
        document.getElementById('app-container').style.display = 'none';
        return false;
    }
}

async function handleLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value.trim();
    
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString()
        });
        
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('token', data.access_token);
            showToast('Успешный вход!', 'success');
            checkAuth();
            loadDashboard();
            checkNotifications();
        } else {
            showToast('Неверный email или пароль', 'error');
        }
    } catch (e) {
        showToast(`Ошибка сети: ${e.message}`, 'error');
    }
}

function logout() {
    localStorage.removeItem('token');
    checkAuth();
}

async function apiRequest(url, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    const token = localStorage.getItem('token');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        if (response.status === 401) {
            logout();
            return null;
        }
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'API request failed');
        }
        return await response.json();
    } catch (e) {
        console.error(e);
        showToast(`Ошибка API: ${e.message}`, 'error');
        return null;
    }
}

// ----------------- DASHBOARD SCREEN -----------------

async function loadDashboard() {
    const data = await apiRequest('/api/dashboard');
    if (!data) return;

    document.getElementById('m-total-sources').innerText = data.sources_count;
    document.getElementById('m-active-sources').innerText = `Активных: ${data.active_sources}`;
    document.getElementById('m-pending-tasks').innerText = data.pending_tasks;
    document.getElementById('m-approved-tasks').innerText = data.completed_tasks;
    const mDocs = document.getElementById('m-total-docs');
    if (mDocs) mDocs.innerText = data.total_docs || 0;

    const tbody = document.querySelector('#dashboard-tasks-table tbody');
    tbody.innerHTML = '';

    if (data.recent_tasks.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 40px 20px;">
                    <div style="font-size: 32px; margin-bottom: 8px;">📭</div>
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px; font-size: 14.5px;">Очередь правового комплаенса пуста</div>
                    <div style="font-size: 12.5px; color: var(--text-muted); max-width: 440px; margin: 0 auto 16px auto;">
                        Добавьте нормативно-правовые акты в мониторинг или запустите проверку для автоматического формирования проектов.
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="openAddSourceModal()">➕ Добавить источник законов</button>
                </td>
            </tr>
        `;
        return;
    }

    data.recent_tasks.forEach(t => {
        const badgeClass = t.status === 'Pending' ? 'badge-pending' : (t.status === 'Approved' ? 'badge-approved' : 'badge-rejected');
        const statusMap = { 'Pending': 'В работе', 'Approved': 'Согласовано', 'Rejected': 'Отклонено' };
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${escapeHtml(t.source_title)}</strong></td>
            <td>
                <span class="badge" style="background-color: ${t.score >= 80 ? 'var(--success-light)' : 'var(--danger-light)'}; color: ${t.score >= 80 ? 'var(--success)' : 'var(--danger)'};">
                    ${t.score}%
                </span>
            </td>
            <td>${t.created_at}</td>
            <td><span class="badge ${badgeClass}">${statusMap[t.status] || t.status}</span></td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick="viewTaskDetail(${t.id})">🔍 Анализ</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// ----------------- MONITORING SCREEN -----------------

let currentLoadedSources = [];
let perDocumentTimerInterval = null;

function formatInterval(hours) {
    if (!hours && hours !== 0) return '24 ч';
    if (hours <= 0.02) return '⚡ 1 мин';
    if (hours <= 0.09) return '⚡ 5 мин';
    if (hours === 1) return '1 час';
    if (hours === 6) return '6 часов';
    if (hours === 12) return '12 часов';
    if (hours === 24) return '24 ч (1 сут)';
    if (hours === 168) return '7 дн (1 нед)';
    return `${hours} ч`;
}

function calculateNextCheckDisplay(lastCheckedStr, intervalHours, isActive) {
    if (!isActive) {
        return '<span style="color: var(--text-muted); font-size: 11.5px;">Отключен</span>';
    }
    if (!lastCheckedStr) {
        return '<span class="badge badge-warning" style="font-size: 11px;">Первичная проверка</span>';
    }
    const lastCheckedDate = new Date(lastCheckedStr);
    const now = new Date();
    const intervalMs = (intervalHours || 24) * 3600 * 1000;
    const nextCheckDate = new Date(lastCheckedDate.getTime() + intervalMs);
    const diffMs = nextCheckDate.getTime() - now.getTime();

    if (diffMs <= 0) {
        return '<span class="badge badge-success" style="font-size: 11px;">Ожидает планового опроса</span>';
    }

    const totalSeconds = Math.floor(diffMs / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    if (hours >= 24) {
        const days = Math.floor(hours / 24);
        return `<span style="font-family: var(--font-code); font-size: 11.5px; color: var(--text-secondary);">Через ${days} дн. ${hours % 24} ч.</span>`;
    } else if (hours > 0) {
        return `<span style="font-family: var(--font-code); font-size: 11.5px; color: var(--text-secondary);">Через ${hours} ч. ${minutes} мин.</span>`;
    } else if (minutes > 0) {
        return `<span style="font-family: var(--font-code); font-size: 11.5px; color: #38bdf8; font-weight: 500;">Через ${minutes} мин. ${seconds} сек.</span>`;
    } else {
        return `<span style="font-family: var(--font-code); font-size: 11.5px; color: #38bdf8; font-weight: 600;">Через ${seconds} сек.</span>`;
    }
}

function updatePerDocumentCountdowns() {
    if (!currentLoadedSources || currentLoadedSources.length === 0) return;
    currentLoadedSources.forEach(s => {
        const el = document.getElementById(`source-countdown-${s.id}`);
        if (el) {
            el.innerHTML = calculateNextCheckDisplay(s.last_checked, s.check_interval_hours, s.is_active);
        }
    });
}

function startPerDocumentTimer() {
    if (perDocumentTimerInterval) clearInterval(perDocumentTimerInterval);
    perDocumentTimerInterval = setInterval(() => {
        if (activeTab === 'monitoring') {
            updatePerDocumentCountdowns();
        }
    }, 1000);
}

async function loadMonitoring() {
    const [data, dashData] = await Promise.all([
        apiRequest('/api/sources'),
        apiRequest('/api/dashboard')
    ]);
    if (dashData) {
        const mTot = document.getElementById('m-total-sources');
        if (mTot) mTot.innerText = dashData.sources_count || 0;
        const mAct = document.getElementById('m-active-sources');
        if (mAct) mAct.innerText = `Активных: ${dashData.active_sources || 0}`;
        const mPen = document.getElementById('m-pending-tasks');
        if (mPen) mPen.innerText = dashData.pending_tasks || 0;
        const mApp = document.getElementById('m-approved-tasks');
        if (mApp) mApp.innerText = dashData.completed_tasks || 0;
        const mDoc = document.getElementById('m-total-docs');
        if (mDoc) mDoc.innerText = dashData.total_docs || 0;
    }
    if (!data) return;
    currentLoadedSources = data;

    const tbody = document.querySelector('#sources-table tbody');
    tbody.innerHTML = '';

    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px 20px;">
                    <div class="metric-icon-box" style="margin: 0 auto 12px auto; width: 44px; height: 44px;">
                        ${getSvgIcon('file', 22)}
                    </div>
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px; font-size: 14.5px;">Источники законодательства еще не добавлены</div>
                    <div style="font-size: 12.5px; color: var(--text-muted); max-width: 440px; margin: 0 auto 16px auto;">
                        Добавьте законы РК (например, с Zan.kz, Adilet или укажите локальный файл) для автоматического отслеживания изменений.
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="openAddSourceModal()">
                        ${getSvgIcon('plus', 13)} Добавить первый источник
                    </button>
                </td>
            </tr>
        `;
        return;
    }

    data.forEach(s => {
        const lastCheckedStr = s.last_checked ? new Date(s.last_checked).toLocaleString('ru-RU') : 'Не проверялось';
        const shaDisplay = s.last_sha256 
            ? `<code style="font-family: var(--font-code); font-size: 11px;" title="SHA-256: ${s.last_sha256}">${s.last_sha256.substring(0, 8)}...</code>`
            : `<span style="color: var(--text-muted); font-size: 11px;">—</span>`;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${escapeHtml(s.title)}</strong></td>
            <td><code style="font-family: var(--font-code); font-size:12px;" title="${escapeHtml(s.url)}">${escapeHtml(s.url.length > 35 ? s.url.substring(0, 32) + '...' : s.url)}</code></td>
            <td><span class="badge badge-secondary" style="font-size: 11px;">${formatInterval(s.check_interval_hours)}</span></td>
            <td style="font-size: 12px; color: var(--text-secondary);">${lastCheckedStr}</td>
            <td id="source-countdown-${s.id}">${calculateNextCheckDisplay(s.last_checked, s.check_interval_hours, s.is_active)}</td>
            <td>${shaDisplay}</td>
            <td>
                <span class="badge ${s.is_active ? 'badge-success' : 'badge-danger'}">
                    ${s.is_active ? 'Активен' : 'Отключен'}
                </span>
            </td>
            <td>
                <div class="source-actions" style="display: flex; gap: 6px;">
                    <button class="btn btn-secondary btn-icon" onclick="exportSourceDocx(${s.id})" title="Выгрузить закон в Word (.docx)">📥</button>
                    <button class="btn btn-secondary btn-icon" onclick="triggerCheck(${s.id})" title="Запустить проверку сейчас">${getSvgIcon('refresh', 13)}</button>
                    <button class="btn btn-danger btn-icon" onclick="deleteSource(${s.id})" title="Удалить закон">${getSvgIcon('trash', 13)}</button>
                </div>
            </td>
        `;
        const editBtn = document.createElement('button');
        editBtn.className = 'btn btn-secondary btn-icon';
        editBtn.title = 'Редактировать параметры источника';
        editBtn.innerHTML = getSvgIcon('edit', 13);
        editBtn.addEventListener('click', () => openEditSourceModal(s.id, s.title, s.url, s.check_interval_hours, s.is_active));
        tr.querySelector('.source-actions').prepend(editBtn);
        tbody.appendChild(tr);
    });

    startPerDocumentTimer();
}

function exportSourceDocx(id) {
    window.open(`/api/sources/${id}/export`, '_blank');
}

function exportInternalDocDocx(id) {
    window.open(`/api/documents/${id}/export`, '_blank');
}

async function triggerCheck(id) {
    const btn = document.activeElement;
    if (btn) btn.innerText = '⏳';
    const res = await apiRequest(`/api/sources/${id}/check`, 'POST');
    if (btn) btn.innerText = '🔄';
    
    if (res) {
        if (res.status === 'changed') {
            showToast(`Обнаружены изменения в документе "${res.source}"! Запущена генерация проектов методологии.`, 'success');
            switchTab('tasks');
        } else if (res.status === 'baseline_established') {
            showToast(`Первоначальный эталон документа "${res.source}" успешно зафиксирован (SHA-256).`, 'info');
            loadMonitoring();
        } else if (res.status === 'unchanged') {
            if (res.audit_task_id) {
                showToast(`Документ "${res.source}" проверен, изменений нет. Запущена плановая проверка соответствия.`, 'success');
                switchTab('tasks');
            } else {
                showToast(`Документ "${res.source}" проверен. Изменений нет (SHA-256 совпадает).`, 'success');
                loadMonitoring();
            }
        } else if (res.status === 'cosmetic_only') {
            if (res.audit_task_id) {
                showToast(`В документе "${res.source}" только косметические изменения. Запущена плановая проверка соответствия.`, 'warning');
                switchTab('tasks');
            } else {
                showToast(`В документе "${res.source}" обнаружены только косметические изменения (даты, подписи). Вызов ИИ пропущен.`, 'warning');
                loadMonitoring();
            }
        } else if (res.status === 'error') {
            showToast(`Ошибка при проверке: ${res.error}`, 'error');
        }
    }
}

async function triggerAllChecks() {
    const data = await apiRequest('/api/sources');
    if (!data) return;
    showToast(`Запущен фоновый обход ${data.length} источников законодательства.`, 'success');
    for (let s of data) {
        await apiRequest(`/api/sources/${s.id}/check`, 'POST');
    }
    loadDashboard();
}

function filterSourcesTable() {
    const q = (document.getElementById('sources-search-input')?.value || '').toLowerCase().trim();
    const rows = document.querySelectorAll('#sources-table tbody tr');
    rows.forEach(r => {
        const text = r.innerText.toLowerCase();
        r.style.display = text.includes(q) ? '' : 'none';
    });
}

function filterTasksTable() {
    const q = (document.getElementById('tasks-search-input')?.value || '').toLowerCase().trim();
    const rows = document.querySelectorAll('#tasks-table tbody tr');
    rows.forEach(r => {
        const text = r.innerText.toLowerCase();
        r.style.display = text.includes(q) ? '' : 'none';
    });
}

function openAddSourceModal() {
    editingSourceId = null;
    editingSourceIsActive = true;
    document.getElementById('source-modal-title').innerText = 'Добавить источник мониторинга';
    document.getElementById('source-title-input').value = '';
    document.getElementById('source-url-input').value = '';
    document.getElementById('source-interval-input').value = '24';
    document.getElementById('add-source-modal').classList.add('active');
}

function openEditSourceModal(id, title, url, interval, isActive) {
    editingSourceId = id;
    editingSourceIsActive = isActive;
    document.getElementById('source-modal-title').innerText = 'Редактировать источник мониторинга';
    document.getElementById('source-title-input').value = title;
    document.getElementById('source-url-input').value = url;
    document.getElementById('source-interval-input').value = interval;
    document.getElementById('add-source-modal').classList.add('active');
}

async function saveSource() {
    const title = document.getElementById('source-title-input').value.trim();
    const url = document.getElementById('source-url-input').value.trim();
    const interval = parseFloat(document.getElementById('source-interval-input').value) || 24;

    if (!title || !url) {
        showToast('Заполните все обязательные поля!', 'error');
        return;
    }

    const res = editingSourceId
        ? await apiRequest(`/api/sources/${editingSourceId}`, 'PUT', {
            title, url, check_interval_hours: interval, is_active: editingSourceIsActive
        })
        : await apiRequest('/api/sources', 'POST', {
            title, url, check_interval_hours: interval
        });

    if (res) {
        closeModal('add-source-modal');
        editingSourceId = null;
        document.getElementById('source-title-input').value = '';
        document.getElementById('source-url-input').value = '';
        loadMonitoring();
    }
}

async function findSourceUrl() {
    const title = document.getElementById('source-title-input').value.trim();
    if (!title) {
        showToast('Сначала укажите название документа!', 'error');
        return;
    }
    if (!editingSourceId) {
        showToast('Поиск ссылки доступен только для существующих источников — сначала сохраните источник.', 'error');
        return;
    }

    const btn = document.getElementById('source-find-url-btn');
    const originalText = btn.innerText;
    btn.innerText = '⏳';
    btn.disabled = true;
    const res = await apiRequest(`/api/sources/${editingSourceId}/find_url`, 'POST');
    btn.innerText = originalText;
    btn.disabled = false;

    if (!res) return;
    if (res.error) {
        showToast(`Ошибка поиска: ${res.error}`, 'error');
        return;
    }
    if (!res.url) {
        showToast('AI не смог уверенно найти ссылку. Проверьте название документа или введите ссылку вручную.', 'warning');
        return;
    }
    document.getElementById('source-url-input').value = res.url;
    showToast(`Найдена ссылка (уверенность: ${res.confidence || '?'}). Проверьте перед сохранением.`, 'success');
}

async function deleteSource(id) {
    if (!confirm('Вы действительно хотите удалить этот источник мониторинга? Все связанные версии будут удалены.')) return;
    const res = await apiRequest(`/api/sources/${id}`, 'DELETE');
    if (res) loadMonitoring();
}

// ----------------- INTERNAL DOCUMENTS SCREEN -----------------

async function loadInternalDocs() {
    const search = document.getElementById('docs-search-input').value;
    const url = search ? `/api/documents?search=${encodeURIComponent(search)}` : '/api/documents';
    const data = await apiRequest(url);
    if (!data) return;

    const tbody = document.querySelector('#documents-table tbody');
    tbody.innerHTML = '';

    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; padding: 40px 20px;">
                    <div class="metric-icon-box" style="margin: 0 auto 12px auto; width: 44px; height: 44px;">
                        ${getSvgIcon('documents', 22)}
                    </div>
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px; font-size: 14.5px;">Внутренние регламенты еще не загружены</div>
                    <div style="font-size: 12.5px; color: var(--text-muted); max-width: 440px; margin: 0 auto 16px auto;">
                        Загрузите правила страхования (.docx, .pdf, .txt) для автоматического векторного анализа влияния изменений законодательства РК.
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="openAddDocModal()">
                        ${getSvgIcon('upload', 13)} Загрузить первый регламент
                    </button>
                </td>
            </tr>
        `;
        return;
    }

    data.forEach(d => {
        const added = d.created_at ? new Date(d.created_at).toLocaleDateString('ru-RU') : 'Давно';
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${escapeHtml(d.title)}</strong></td>
            <td><span class="badge badge-info">${escapeHtml(d.category)}</span></td>
            <td>${added}</td>
            <td>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-secondary btn-sm" onclick="exportInternalDocDocx(${d.id})" title="Выгрузить регламент в Word (.docx)">
                        📥 Word
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="inspectRegulationInDrawer(${d.id})" title="Быстрый просмотр регламента">
                        ${getSvgIcon('search', 13)} Просмотр
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="suggestSourcesForDocument(${d.id})" title="Подобрать законы РК для мониторинга">
                        ${getSvgIcon('file', 13)} Законы РК
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteDocument(${d.id})" title="Удалить регламент">
                        ${getSvgIcon('trash', 13)}
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function openAddDocModal() {
    document.getElementById('add-doc-modal').classList.add('active');
}

async function saveDocument() {
    const title = document.getElementById('doc-title-input').value.trim();
    const category = document.getElementById('doc-category-input').value;
    const fileInput = document.getElementById('doc-file-input');
    const content = document.getElementById('doc-content-input').value.trim();

    if (!title) {
        showToast('Укажите название документа!', 'error');
        return;
    }

    let res;
    if (fileInput.files.length > 0) {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('category', category);
        formData.append('file', fileInput.files[0]);

        const token = localStorage.getItem('token');
        try {
            const response = await fetch('/api/documents/upload', {
                method: 'POST',
                headers: token ? { 'Authorization': `Bearer ${token}` } : {},
                body: formData
            });
            if (response.status === 401) {
                logout();
                return;
            }
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Не удалось загрузить файл');
            }
            res = await response.json();
        } catch (e) {
            showToast(`Ошибка загрузки: ${e.message}`, 'error');
            return;
        }
    } else {
        if (!content) {
            showToast('Прикрепите файл или вставьте текст документа!', 'error');
            return;
        }
        res = await apiRequest('/api/documents', 'POST', {
            title, category, content_markdown: content
        });
    }

    if (res) {
        closeModal('add-doc-modal');
        document.getElementById('doc-title-input').value = '';
        document.getElementById('doc-content-input').value = '';
        fileInput.value = '';
        loadInternalDocs();
    }
}

async function suggestSourcesForDocument(id) {
    showToast('AI анализирует документ и ищет актуальные законы...', 'success');
    const res = await apiRequest(`/api/documents/${id}/suggest_sources`, 'POST');
    if (!res) return;

    const list = document.getElementById('suggest-sources-list');
    list.innerHTML = '';

    const suggestions = res.suggestions || [];
    if (res.error) {
        list.innerHTML = `<div style="color: var(--danger);">Ошибка обращения к AI: ${escapeHtml(res.error)}<br><span style="font-size:11px; color: var(--text-muted);">Проверьте квоту/биллинг Gemini API или доступность модели.</span></div>`;
    } else if (suggestions.length === 0) {
        list.innerHTML = '<div style="color: var(--text-muted); padding: 20px; text-align: center;">AI не смог определить законы, применимые к этому документу.</div>';
    } else {
        suggestions.forEach(s => {
            const div = document.createElement('div');
            div.className = 'panel';
            div.style.padding = '14px 16px';
            div.style.marginBottom = '10px';
            div.innerHTML = `
                <div style="font-weight:600; display:flex; justify-content:space-between; gap: 10px;">
                    <span style="display:inline-flex; align-items:center; gap:6px;">
                        ${getSvgIcon('file', 14)} ${escapeHtml(s.title || 'Без названия')}
                    </span>
                    <span class="badge badge-info">${escapeHtml(s.confidence || 'нормально')}</span>
                </div>
                <div style="font-size:12.5px; color:var(--text-secondary); margin-top:4px;">${escapeHtml(s.reason || '')}</div>
                <div style="font-size:12px; margin-top:6px; word-break: break-all; color: var(--text-muted);">${s.url ? escapeHtml(s.url) : 'Ссылка не найдена — добавьте вручную'}</div>
                <div class="suggestion-actions" style="display:flex; justify-content:flex-end; margin-top:8px;"></div>
            `;
            const btn = document.createElement('button');
            btn.className = 'btn btn-primary btn-sm';
            btn.innerHTML = `${getSvgIcon('plus', 13)} Добавить в мониторинг`;
            btn.addEventListener('click', () => approveSourceSuggestion(btn, s.title || '', s.url || ''));
            div.querySelector('.suggestion-actions').appendChild(btn);
            list.appendChild(div);
        });
    }

    document.getElementById('suggest-sources-modal').classList.add('active');
}

async function approveSourceSuggestion(btn, title, url) {
    if (!url) {
        showToast('Сначала укажите реальную ссылку на источник вручную (через "Мониторинг законов").', 'error');
        return;
    }
    const res = await apiRequest('/api/sources', 'POST', {
        title, url, check_interval_hours: 24
    });
    if (res) {
        btn.disabled = true;
        btn.innerHTML = `${getSvgIcon('check', 13)} Добавлено`;
        showToast(`Источник "${title}" добавлен в мониторинг.`, 'success');
    }
}

async function deleteDocument(id) {
    if (!confirm('Удалить внутренний регламент компании?')) return;
    const res = await apiRequest(`/api/documents/${id}`, 'DELETE');
    if (res) loadInternalDocs();
}

// ----------------- TASKS SCREEN -----------------

function showTasksList() {
    document.getElementById('tasks-list-panel').style.display = 'block';
    document.getElementById('task-detail-panel').style.display = 'none';
    loadTasks();
}

async function loadTasks() {
    const data = await apiRequest('/api/tasks');
    if (!data) return;

    const tbody = document.querySelector('#tasks-table tbody');
    tbody.innerHTML = '';

    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 40px 20px;">
                    <div class="metric-icon-box" style="margin: 0 auto 12px auto; width: 44px; height: 44px;">
                        ${getSvgIcon('tasks', 22)}
                    </div>
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px; font-size: 14.5px;">Задач на анализ пока нет</div>
                    <div style="font-size: 12.5px; color: var(--text-muted); max-width: 440px; margin: 0 auto 16px auto;">
                        При обнаружении изменений в законах или при плановом аудите здесь появятся задачи с готовыми проектами документов.
                    </div>
                    <button class="btn btn-secondary btn-sm" onclick="switchTab('monitoring')">
                        Перейти в мониторинг законов →
                    </button>
                </td>
            </tr>
        `;
        return;
    }

    data.forEach(t => {
        const badgeClass = t.status === 'Pending' ? 'badge-pending' : (t.status === 'Approved' ? 'badge-approved' : 'badge-rejected');
        const statusMap = { 'Pending': 'В работе', 'Approved': 'Согласовано', 'Rejected': 'Отклонено' };
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${t.id}</td>
            <td><strong>${escapeHtml(t.source_title)}</strong></td>
            <td>${t.created_at}</td>
            <td>${t.has_drafts ? '<span class="badge badge-success" style="font-size: 11px;">Сформированы</span>' : '<span class="badge badge-warning" style="font-size: 11px;">В процессе</span>'}</td>
            <td><span class="badge ${badgeClass}">${statusMap[t.status] || t.status}</span></td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick="viewTaskDetail(${t.id})">
                    ${getSvgIcon('search', 13)} Подробнее
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function viewTaskDetail(id) {
    activeTaskId = id;
    const t = await apiRequest(`/api/tasks/${id}`);
    if (!t) return;

    currentTaskData = t;
    document.getElementById('tasks-list-panel').style.display = 'none';
    document.getElementById('task-detail-panel').style.display = 'block';

    // Update Topbar Meta
    const titleEl = document.getElementById('diff-law-title');
    if (titleEl) titleEl.innerText = t.source_title || `Задача #${t.id}`;
    
    const badgeEl = document.getElementById('diff-version-badge');
    if (badgeEl) {
        badgeEl.innerText = `Редакция v${t.new_version?.version_num || 2}`;
        badgeEl.className = 'badge badge-info';
    }

    // Insert Diff Side-by-Side HTML
    const diffContainer = document.getElementById('task-diff-container');
    diffContainer.innerHTML = t.diff_html || '<div style="padding: 30px; text-align: center; color: var(--text-muted);">Разница между редакциями не обнаружена.</div>';

    // Build Left Table of Contents for Articles
    buildDiffArticleToc();

    // Show Drafts - load active tab
    activeDraftTab = 'rules';
    switchDraftTab('rules');
}

function buildDiffArticleToc() {
    const diffContainer = document.getElementById('task-diff-container');
    const tocList = document.getElementById('diff-toc-list');
    const changedBadge = document.getElementById('diff-changed-articles-count');
    if (!diffContainer || !tocList) return;

    tocList.innerHTML = '';
    const rows = diffContainer.querySelectorAll('tr[data-article]');
    
    // Group articles
    const articleMap = new Map();
    rows.forEach(r => {
        const artName = r.getAttribute('data-article') || 'Текст документа';
        if (!articleMap.has(artName)) {
            articleMap.set(artName, { firstRow: r, hasChanges: false, changeCount: 0 });
        }
        const isChanged = r.classList.contains('diff-row-changed');
        if (isChanged) {
            const entry = articleMap.get(artName);
            entry.hasChanges = true;
            entry.changeCount++;
        }
    });

    let totalChangedArticles = 0;
    articleMap.forEach((entry, artName) => {
        if (entry.hasChanges) totalChangedArticles++;

        const li = document.createElement('li');
        li.className = `diff-toc-item ${entry.hasChanges ? 'has-changes' : ''}`;
        
        const shortName = artName.length > 28 ? artName.substring(0, 26) + '…' : artName;
        const badge = entry.hasChanges 
            ? `<span class="badge badge-danger" style="font-size: 10px; padding: 2px 6px;">${entry.changeCount} изм.</span>`
            : `<span style="color: var(--text-muted); font-size: 11px;">✓</span>`;

        li.innerHTML = `
            <span title="${escapeHtml(artName)}">${escapeHtml(shortName)}</span>
            ${badge}
        `;

        li.addEventListener('click', () => {
            document.querySelectorAll('.diff-toc-item').forEach(el => el.classList.remove('active'));
            li.classList.add('active');
            entry.firstRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Temporary flash highlight
            entry.firstRow.style.outline = '2px solid var(--primary)';
            setTimeout(() => { entry.firstRow.style.outline = ''; }, 1500);
        });

        tocList.appendChild(li);
    });

    if (changedBadge) {
        changedBadge.innerText = `${totalChangedArticles} изм.`;
        changedBadge.className = totalChangedArticles > 0 ? 'badge badge-danger' : 'badge badge-success';
    }
}

function openAiRiskModal() {
    const modal = document.getElementById('ai-risk-modal');
    const modalBody = document.getElementById('ai-risk-modal-body');
    if (!modal || !modalBody || !currentTaskData) return;

    const t = currentTaskData;
    const analysis = t.analysis || {};
    const whatChanged = analysis.what_changed || [];
    const risks = analysis.key_risks || [];
    const requirements = analysis.actionable_requirements || [];
    const departments = analysis.affected_departments || [];

    let html = `
        <div class="panel" style="margin-bottom: 0; padding: 16px;">
            <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 12px;">
                Закон: <strong>${escapeHtml(t.source_title || 'НПА')}</strong>
            </div>
    `;

    if (whatChanged.length > 0) {
        html += `
            <div style="margin-bottom: 14px;">
                <h4 style="font-size: 13px; font-weight: 700; color: #93c5fd; margin-bottom: 6px;">📌 Что изменилось в законодательстве:</h4>
                <ul style="margin: 0; padding-left: 18px; font-size: 13px; line-height: 1.5;">
                    ${whatChanged.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (risks.length > 0) {
        html += `
            <div style="margin-bottom: 14px;">
                <h4 style="font-size: 13px; font-weight: 700; color: #fca5a5; margin-bottom: 6px;">⚠️ Регуляторные риски:</h4>
                <ul style="margin: 0; padding-left: 18px; font-size: 13px; line-height: 1.5;">
                    ${risks.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (requirements.length > 0) {
        html += `
            <div style="margin-bottom: 14px;">
                <h4 style="font-size: 13px; font-weight: 700; color: #6ee7b7; margin-bottom: 6px;">✅ Что необходимо сделать компании:</h4>
                <ul style="margin: 0; padding-left: 18px; font-size: 13px; line-height: 1.5;">
                    ${requirements.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (departments.length > 0) {
        html += `
            <div>
                <h4 style="font-size: 13px; font-weight: 700; color: #c084fc; margin-bottom: 6px;">🏢 Затронутые подразделения:</h4>
                <div style="display: flex; flex-direction: column; gap: 6px;">
                    ${departments.map(d => `
                        <div style="background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 6px; font-size: 12.5px;">
                            <strong>${escapeHtml(d.department)}:</strong> ${escapeHtml(d.reason || '')}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    if (!whatChanged.length && !risks.length && !requirements.length) {
        html += `
            <div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px;">
                AI-анализ рисков ещё не сгенерирован для этого изменения.
                <div style="margin-top: 12px;">
                    <button class="btn btn-primary btn-sm" onclick="regenerateTask(${t.id}); closeAiRiskModal();">
                        ⚡ Сгенерировать AI-справку сейчас
                    </button>
                </div>
            </div>
        `;
    }

    html += `</div>`;
    modalBody.innerHTML = html;
    modal.style.display = 'flex';
}

function closeAiRiskModal() {
    const modal = document.getElementById('ai-risk-modal');
    if (modal) modal.style.display = 'none';
}

function switchDraftTab(tabName) {
    activeDraftTab = tabName;
    document.querySelectorAll('.btn-draft-tab').forEach(btn => {
        if (btn.getAttribute('data-draft') === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    const drafts = currentTaskData ? currentTaskData.drafts : {};
    const textarea = document.getElementById('draft-active-textarea');
    
    if (!drafts) {
        textarea.value = 'Черновики отсутствуют. Запустите генерацию.';
        return;
    }

    if (tabName === 'rules') {
        textarea.value = drafts.rules_changes || '';
    } else if (tabName === 'memo') {
        textarea.value = drafts.memo || '';
    } else if (tabName === 'board') {
        textarea.value = drafts.board_letter || '';
    } else if (tabName === 'board-directors') {
        textarea.value = drafts.board_directors_letter || '';
    } else if (tabName === 'plan') {
        // Implementation plan is a list
        const plan = drafts.implementation_plan || [];
        textarea.value = Array.isArray(plan) ? plan.map(p => `Этап: ${p.step}\nСрок: ${p.deadline}\nОтветственный: ${p.owner}\n`).join('\n') : plan;
    } else if (tabName === 'checklist') {
        const list = drafts.checklist || [];
        textarea.value = Array.isArray(list) ? list.map(l => `- [ ] ${l.item}`).join('\n') : list;
    }
}

async function saveDraftChange() {
    const val = document.getElementById('draft-active-textarea').value.trim();
    if (!currentTaskData || !currentTaskData.drafts) return;

    const keyMap = {
        'rules': 'rules_changes',
        'memo': 'memo',
        'board': 'board_letter',
        'board-directors': 'board_directors_letter'
    };

    if (activeDraftTab === 'rules' || activeDraftTab === 'memo' || activeDraftTab === 'board' || activeDraftTab === 'board-directors') {
        currentTaskData.drafts[keyMap[activeDraftTab]] = val;
    } else if (activeDraftTab === 'plan') {
        // Parse simple text lines back to plan array
        const blocks = val.split('\n\n');
        const planArray = [];
        blocks.forEach(block => {
            const lines = block.split('\n');
            const stepObj = { step: '', deadline: '', owner: '' };
            lines.forEach(line => {
                if (line.startsWith('Этап:')) stepObj.step = line.replace('Этап:', '').trim();
                if (line.startsWith('Срок:')) stepObj.deadline = line.replace('Срок:', '').trim();
                if (line.startsWith('Ответственный:')) stepObj.owner = line.replace('Ответственный:', '').trim();
            });
            if (stepObj.step) planArray.push(stepObj);
        });
        currentTaskData.drafts.implementation_plan = planArray;
    } else if (activeDraftTab === 'checklist') {
        const lines = val.split('\n');
        const checklistArray = [];
        lines.forEach(line => {
            const clean = line.replace(/^-\s*\[\s*\]\s*/, '').trim();
            if (clean) checklistArray.push({ item: clean });
        });
        currentTaskData.drafts.checklist = checklistArray;
    }

    const res = await apiRequest(`/api/tasks/${activeTaskId}/save_drafts`, 'POST', currentTaskData.drafts);
    if (res) {
        showToast('Изменения проекта сохранены успешно!', 'success');
    }
}

function exportActiveDocx() {
    const docTypeMap = {
        'rules': 'rules',
        'memo': 'memo',
        'board': 'board_letter',
        'board-directors': 'board_directors_letter',
        'plan': 'plan',
        'checklist': 'checklist'
    };
    const t = docTypeMap[activeDraftTab];
    window.open(`/api/tasks/${activeTaskId}/export/${t}`, '_blank');
}

function exportComparativeTableDocx() {
    if (!activeTaskId) {
        showToast('Задача не выбрана', 'error');
        return;
    }
    window.open(`/api/tasks/${activeTaskId}/export_table`, '_blank');
}

function copyActiveDraftToClipboard() {
    const textarea = document.getElementById('draft-active-textarea');
    if (!textarea || !textarea.value.trim()) {
        showToast('Текст проекта пуст', 'warning');
        return;
    }
    const btn = document.activeElement;
    navigator.clipboard.writeText(textarea.value).then(() => {
        if (btn && btn.tagName === 'BUTTON') {
            const oldText = btn.innerText;
            btn.classList.add('copied');
            btn.innerText = '✓ Скопировано';
            setTimeout(() => {
                btn.classList.remove('copied');
                btn.innerText = oldText;
            }, 2000);
        }
        showToast('Текст проекта скопирован в буфер обмена 📋', 'success');
    }).catch(() => {
        showToast('Не удалось скопировать в буфер', 'error');
    });
}

function toggleDiffFocus() {
    const container = document.getElementById('task-diff-container');
    const btn = document.getElementById('btn-toggle-diff-focus');
    if (!container || !btn) return;

    container.classList.toggle('focus-changes');
    const isFocus = container.classList.contains('focus-changes');
    btn.innerText = isFocus ? '📄 Показать весь документ' : '🔍 Только изменения';
    btn.classList.toggle('btn-primary', isFocus);
    btn.classList.toggle('btn-secondary', !isFocus);
}

async function sendTelegramTestNotification() {
    showToast('Отправка тестового алерта в Telegram...', 'info');
    const res = await apiRequest('/api/notifications/telegram-test', 'POST');
    if (res) {
        if (res.status === 'success') {
            showToast('✅ ' + res.message, 'success');
        } else if (res.status === 'warning') {
            showToast('⚠️ ' + res.message, 'warning');
        }
        loadNotifications();
    }
}

async function approveTask(id) {
    if (!confirm('Вы одобряете разработанные изменения регламентов? Решение будет добавлено в корпоративную память AI.')) return;
    const res = await apiRequest(`/api/tasks/${id}`, 'PUT', { status: 'Approved' });
    if (res) {
        showToast('Задача успешно согласована. AI Агент обучен на данном решении.', 'success');
        viewTaskDetail(id);
    }
}

function openRejectModal() {
    document.getElementById('reject-task-modal').classList.add('active');
    document.getElementById('btn-confirm-reject').onclick = confirmRejectTask;
}

async function confirmRejectTask() {
    const reason = document.getElementById('task-reject-reason-input').value.trim();
    if (!reason) {
        showToast('Укажите причину отклонения!', 'error');
        return;
    }

    const res = await apiRequest(`/api/tasks/${activeTaskId}`, 'PUT', {
        status: 'Rejected',
        reject_reason: reason
    });

    if (res) {
        closeModal('reject-task-modal');
        document.getElementById('task-reject-reason-input').value = '';
        showToast('Проект отклонен. Причина сохранена в памяти AI для корректировки следующих промптов.', 'warning');
        viewTaskDetail(activeTaskId);
    }
}

async function regenerateTask(id) {
    const btn = document.activeElement;
    if (btn) btn.innerText = '⏳ Регенерация...';
    const res = await apiRequest(`/api/tasks/${id}/regenerate`, 'POST');
    if (btn) btn.innerText = '🔄 Перегенерировать ИИ';

    if (res) {
        showToast('Регенерация запущена в фоне (может занять до минуты). Откройте задачу заново, чтобы увидеть результат.', 'success');
        viewTaskDetail(id);
    }
}

// ----------------- CONNECTIONS GRAPH (relations) -----------------

let currentGraphScale = 1.0;
let graphActiveFilter = 'all';

function filterGraphCategory(cat) {
    graphActiveFilter = cat;
    document.querySelectorAll('.graph-toolbar button[id^="graph-filter-btn-"]').forEach(b => {
        b.classList.remove('active');
    });
    const activeBtn = document.getElementById(`graph-filter-btn-${cat}`);
    if (activeBtn) activeBtn.classList.add('active');
    drawRelationsGraph();
}

function zoomGraph(factor) {
    currentGraphScale = Math.max(0.4, Math.min(2.5, currentGraphScale * factor));
    const svg = document.getElementById('relations-graph-svg');
    if (svg) {
        const baseW = 1000 * currentGraphScale;
        const baseH = 540 * currentGraphScale;
        const offsetX = (1000 - baseW) / 2;
        const offsetY = (540 - baseH) / 2;
        svg.setAttribute('viewBox', `${offsetX} ${offsetY} ${baseW} ${baseH}`);
    }
}

function resetGraphZoom() {
    currentGraphScale = 1.0;
    const svg = document.getElementById('relations-graph-svg');
    if (svg) {
        svg.setAttribute('viewBox', '0 0 1000 540');
    }
}

function inspectGraphNode(node, graphData) {
    const insp = document.getElementById('graph-inspector');
    if (!insp) return;

    const icons = {
        'law': '📜',
        'task': '⚖️',
        'rule': '📂',
        'clause': '📝',
        'dept': '🏢'
    };
    const typeNames = {
        'law': 'Законодательный акт РК',
        'task': 'Комплаенс-задача',
        'rule': 'Внутренний регламент компании',
        'clause': 'Пункт / Раздел регламента под изменением',
        'dept': 'Затронутый департамент'
    };

    document.getElementById('graph-insp-icon').innerText = icons[node.type] || '📌';
    document.getElementById('graph-insp-title').innerText = `${node.label} (${typeNames[node.type] || node.type})`;

    // Find linked nodes
    const links = (graphData.links || []).filter(l => l.source === node.id || l.target === node.id);
    const connectedNodeIds = links.map(l => l.source === node.id ? l.target : l.source);
    const connectedNodes = (graphData.nodes || []).filter(n => connectedNodeIds.includes(n.id));

    let linksHtml = '';
    if (connectedNodes.length > 0) {
        linksHtml = '<div style="margin-top: 10px; font-weight: 600; color: var(--text-primary);">Связанные объекты:</div><ul style="margin-top: 6px; padding-left: 20px; display: flex; flex-direction: column; gap: 4px;">';
        connectedNodes.forEach(cn => {
            linksHtml += `<li><span style="color: var(--primary-hover); font-weight: 500;">${icons[cn.type] || '•'} ${escapeHtml(cn.label)}</span> <span style="font-size: 11px; color: var(--text-muted);">(${cn.type.toUpperCase()})</span></li>`;
        });
        linksHtml += '</ul>';
    } else {
        linksHtml = '<div style="margin-top: 8px; color: var(--text-muted);">Нет прямых связей для этого узла.</div>';
    }

    let extraDetails = '';
    if (node.details && node.details.summary) {
        extraDetails = `<div style="margin-top: 10px; padding: 8px 12px; background: rgba(255,255,255,0.03); border-radius: 6px; font-size: 12px;"><strong>Суть правок:</strong> ${escapeHtml(node.details.summary)}</div>`;
    }

    document.getElementById('graph-insp-body').innerHTML = `
        <div>Категория: <span class="badge badge-info">${typeNames[node.type] || node.type}</span></div>
        ${extraDetails}
        ${linksHtml}
    `;

    insp.style.display = 'block';
}

async function drawRelationsGraph() {
    const svg = document.getElementById('relations-graph-svg');
    svg.innerHTML = '';
    resetGraphZoom();
    svg.setAttribute('viewBox', '0 0 1000 540');
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

    const data = await apiRequest('/api/relations');
    if (!data || !data.nodes || data.nodes.length === 0) {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('transform', 'translate(500, 230)');
        
        const icon = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        icon.setAttribute('text-anchor', 'middle');
        icon.setAttribute('y', '-20');
        icon.setAttribute('font-size', '36');
        icon.textContent = '🕸️';
        g.appendChild(icon);

        const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        title.setAttribute('text-anchor', 'middle');
        title.setAttribute('y', '20');
        title.setAttribute('fill', '#f8fafc');
        title.setAttribute('font-size', '15');
        title.setAttribute('font-weight', '600');
        title.textContent = 'Карта регуляторных связей формируется автоматически';
        g.appendChild(title);

        const sub = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        sub.setAttribute('text-anchor', 'middle');
        sub.setAttribute('y', '45');
        sub.setAttribute('fill', '#94a3b8');
        sub.setAttribute('font-size', '12.5');
        sub.textContent = 'Добавьте законы РК и регламенты компании для построения сквозного графа зависимостей.';
        g.appendChild(sub);

        svg.appendChild(g);
        return;
    }

    // Filter nodes if category is selected
    let nodesToDraw = data.nodes;
    if (graphActiveFilter !== 'all') {
        nodesToDraw = data.nodes.filter(n => n.type === graphActiveFilter);
    }
    const nodeIdsToDraw = new Set(nodesToDraw.map(n => n.id));

    // Layout: 5 Columns (Закон -> Задача -> Регламент -> Пункт правил -> Департамент)
    const columnX = { law: 80, task: 290, rule: 510, clause: 740, dept: 940 };
    const byType = {};
    nodesToDraw.forEach(n => {
        (byType[n.type] = byType[n.type] || []).push(n);
    });

    const positioned = {};
    const topPadding = 40;
    const usableHeight = 460;
    Object.keys(byType).forEach(type => {
        const list = byType[type];
        list.forEach((n, i) => {
            positioned[n.id] = {
                ...n,
                x: columnX[type] ?? 500,
                y: topPadding + (i + 0.5) * (usableHeight / list.length)
            };
        });
    });

    // Render links with smooth Bezier paths
    data.links.forEach(l => {
        if (nodeIdsToDraw.has(l.source) && nodeIdsToDraw.has(l.target)) {
            const sNode = positioned[l.source];
            const tNode = positioned[l.target];
            if (sNode && tNode) {
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                const dx = (tNode.x - sNode.x) * 0.5;
                const d = `M ${sNode.x} ${sNode.y} C ${sNode.x + dx} ${sNode.y}, ${tNode.x - dx} ${tNode.y}, ${tNode.x} ${tNode.y}`;
                path.setAttribute('d', d);
                path.setAttribute('class', 'graph-edge');
                path.setAttribute('fill', 'none');
                svg.appendChild(path);
            }
        }
    });

    // Render nodes
    Object.values(positioned).forEach(n => {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', `graph-node ${n.type}`);
        g.setAttribute('transform', `translate(${n.x}, ${n.y})`);

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('r', '9');
        g.appendChild(circle);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('dx', '14');
        text.setAttribute('dy', '4');
        text.textContent = n.label;
        g.appendChild(text);

        // Click interaction -> inspect node
        g.addEventListener('click', () => {
            inspectGraphNode(n, data);
        });

        svg.appendChild(g);
    });
}



// ----------------- PROMPT ZONE SCREEN -----------------

async function loadPromptsZone() {
    const data = await apiRequest('/api/prompts');
    if (!data) return;

    const list = document.getElementById('prompts-list');
    list.innerHTML = '';

    data.forEach(p => {
        const names = {
            'system_prompt': 'Главная роль (System Prompt)',
            'legal_prompt': 'Анализ законов (Legal Prompt)',
            'draft_prompt': 'Подготовка документов (Draft Prompt)',
            'review_prompt': 'Рецензирование (Review Prompt)',
            'audit_prompt': 'Плановый аудит (Audit Prompt)',
            'source_suggestion_prompt': 'Подбор законов для регламента (Source Suggestion)'
        };
        
        const item = document.createElement('div');
        item.className = `prompt-list-item ${activePromptKey === p.key ? 'active' : ''}`;
        item.onclick = () => selectPrompt(p.key, p.content, p.version);
        item.innerHTML = `
            <div class="prompt-key-title">${names[p.key] || p.key}</div>
            <div style="font-size:12px; color:hsl(var(--text-secondary)); display:flex; justify-content:space-between; margin-top:4px;">
                <span>Ключ: ${p.key}</span>
                <span class="prompt-version-tag">v${p.version}</span>
            </div>
        `;
        list.appendChild(item);
    });

    if (data.length > 0 && !activePromptKey) {
        // Select first automatically
        selectPrompt(data[0].key, data[0].content, data[0].version);
    }
}

function selectPrompt(key, content, version) {
    activePromptKey = key;
    document.querySelectorAll('.prompt-list-item').forEach(item => {
        if (item.querySelector('.prompt-key-title').innerText.includes(key) || item.innerText.includes(key)) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    const names = {
        'system_prompt': 'Главная роль (System Prompt)',
        'legal_prompt': 'Анализ законов (Legal Prompt)',
        'draft_prompt': 'Подготовка документов (Draft Prompt)',
        'review_prompt': 'Рецензирование (Review Prompt)',
        'audit_prompt': 'Плановый аудит (Audit Prompt)',
        'source_suggestion_prompt': 'Подбор законов для регламента (Source Suggestion)'
    };
    
    document.getElementById('active-prompt-title').innerText = names[key] || key;

    document.getElementById('active-prompt-version').innerText = `v${version}`;
    document.getElementById('active-prompt-editor').value = content;
    
    // Refresh prompt list active classes
    loadPromptsZoneListOnly(key, version);
}

function loadPromptsZoneListOnly(activeKey, activeVersion) {
    const items = document.querySelectorAll('.prompt-list-item');
    items.forEach(item => {
        if (item.innerHTML.includes(`Ключ: ${activeKey}`)) {
            item.classList.add('active');
            item.querySelector('.prompt-version-tag').innerText = `v${activeVersion}`;
        } else {
            item.classList.remove('active');
        }
    });
}

async function savePromptContent() {
    const val = document.getElementById('active-prompt-editor').value;
    if (!activePromptKey) return;

    const res = await apiRequest(`/api/prompts/${activePromptKey}`, 'PUT', { content: val });
    if (res) {
        showToast('Промпт сохранен. Новая версия добавлена в лог истории.', 'success');
        selectPrompt(res.key, res.content, res.version);
        loadPromptsZone();
    }
}

// ----------------- AI CHAT SCREEN -----------------

async function sendChatMessage() {
    const input = document.getElementById('chat-input-field');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';

    const box = document.getElementById('chat-messages-box');
    
    // Append User message
    const uDiv = document.createElement('div');
    uDiv.className = 'chat-bubble user';
    uDiv.innerText = msg;
    box.appendChild(uDiv);
    box.scrollTop = box.scrollHeight;

    // Append loading assistant bubble
    const aDiv = document.createElement('div');
    aDiv.className = 'chat-bubble assistant';
    aDiv.innerText = 'AI Методолог размышляет... ⏳';
    box.appendChild(aDiv);
    box.scrollTop = box.scrollHeight;

    const res = await apiRequest('/api/chat', 'POST', { message: msg });
    
    if (res) {
        aDiv.innerText = res.response;
    } else {
        aDiv.innerText = 'Ошибка отправки запроса.';
    }
    box.scrollTop = box.scrollHeight;
}

function handleChatKeyPress(e) {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
}

function sendQuickChatMessage(text) {
    const input = document.getElementById('chat-input-field');
    if (!input) return;
    input.value = text;
    sendChatMessage();
}


// ----------------- MODALS HELPERS -----------------

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// ----------------- NOTIFICATIONS & SCHEDULER CONTROLLER -----------------

async function checkNotifications() {
    const data = await apiRequest('/api/notifications?limit=10');
    if (!data) return;

    const badge = document.getElementById('notification-badge-count');
    if (badge) {
        if (data.unread_count > 0) {
            badge.innerText = data.unread_count > 99 ? '99+' : data.unread_count;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }
}

async function openNotificationsModal() {
    const data = await apiRequest('/api/notifications?limit=50');
    if (!data) return;

    const list = document.getElementById('notifications-list');
    const countBadge = document.getElementById('notifications-modal-count');
    if (countBadge) countBadge.innerText = `${data.unread_count} новых`;

    list.innerHTML = '';
    if (!data.notifications || data.notifications.length === 0) {
        list.innerHTML = '<div style="padding: 30px; text-align: center; color: hsl(var(--text-muted));">Уведомлений нет. Все изменения под контролем!</div>';
    } else {
        data.notifications.forEach(n => {
            const div = document.createElement('div');
            div.className = `notification-item ${n.is_read ? '' : 'unread'} severity-${n.severity || 'normal'}`;
            
            const typeIcon = {
                'change_detected': '🚨',
                'audit_completed': '📋',
                'quality_warning': '⚠️',
                'error': '❌',
                'info': 'ℹ️'
            }[n.type] || '🔔';

            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
                    <div style="font-weight: 600; font-size: 14px; display: flex; align-items: center; gap: 6px;">
                        <span>${typeIcon}</span>
                        <span>${escapeHtml(n.title)}</span>
                    </div>
                    ${!n.is_read ? `<button class="btn btn-secondary" style="font-size: 11px; padding: 2px 8px;" onclick="markNotificationRead(${n.id}, event)">Прочитано</button>` : ''}
                </div>
                <div style="font-size: 13px; color: hsl(var(--text-secondary)); margin-top: 4px;">${escapeHtml(n.message)}</div>
                <div class="notification-meta" style="margin-top: 8px;">
                    <span>${n.created_at}</span>
                    ${n.link_url ? `<a href="${n.link_url}" onclick="closeModal('notifications-modal')" style="color: hsl(var(--color-primary-hover)); text-decoration: none; font-weight: 600;">Перейти в раздел →</a>` : ''}
                </div>
            `;
            list.appendChild(div);
        });
    }

    document.getElementById('notifications-modal').classList.add('active');
}

async function markNotificationRead(id, event) {
    if (event) event.stopPropagation();
    const res = await apiRequest(`/api/notifications/${id}/read`, 'PUT');
    if (res) {
        checkNotifications();
        openNotificationsModal();
    }
}

async function markAllNotificationsRead() {
    const res = await apiRequest('/api/notifications/read-all', 'POST');
    if (res) {
        showToast('Все уведомления отмечены как прочитанные', 'success');
        checkNotifications();
        openNotificationsModal();
    }
}

async function loadSchedulerStatus() {
    const data = await apiRequest('/api/scheduler/status');
    if (!data) return;

    const stateText = document.getElementById('scheduler-state-text');
    const detailsText = document.getElementById('scheduler-details-text');
    if (stateText && detailsText) {
        stateText.innerText = data.is_running ? 'Активен' : 'Остановлен';
        stateText.style.color = data.is_running ? '#4ade80' : '#ef4444';
        detailsText.innerText = `Интервал фонового сканирования: ${data.interval_seconds} сек. | Последний запуск: ${data.last_run || 'Ожидает запуска'} | Выполнено проверок: ${data.total_checks_run}`;
    }
}

async function runSchedulerNow() {
    const btn = document.getElementById('btn-run-scheduler');
    if (btn) {
        btn.disabled = true;
        btn.innerText = '⏳ Проверка...';
    }
    const res = await apiRequest('/api/scheduler/run-now', 'POST');
    if (btn) {
        btn.disabled = false;
        btn.innerText = '⚡ Запустить плановый опрос сейчас';
    }
    if (res) {
        const s = res.summary || {};
        showToast(`Шедулер завершил опрос: проверено источников: ${s.checked}, изменений: ${s.changes_found}, плановых аудитов: ${s.audits_run}`, 'success');
        loadMonitoring();
        checkNotifications();
        loadSchedulerStatus();
    }
}

// ----------------- SANDBOX / DIFF LAB -----------------

function initSandboxListeners() {
    const oldTextEl = document.getElementById('sandbox-old-text');
    const newTextEl = document.getElementById('sandbox-new-text');

    if (oldTextEl) {
        oldTextEl.oninput = () => updateSandboxCharCounters('old');
    }
    if (newTextEl) {
        newTextEl.oninput = () => updateSandboxCharCounters('new');
    }
}

function updateSandboxCharCounters(side) {
    const text = document.getElementById(`sandbox-${side}-text`)?.value || '';
    const charsEl = document.getElementById(`sandbox-${side}-chars`);
    if (charsEl) {
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        charsEl.innerText = `${text.length} симв. | ${words} слов`;
    }
}

function switchSandboxInputMode(side, mode) {
    const textBtn = document.getElementById(`sb-mode-${side}-text`);
    const fileBtn = document.getElementById(`sb-mode-${side}-file`);
    const urlBtn = document.getElementById(`sb-mode-${side}-url`);

    [textBtn, fileBtn, urlBtn].forEach(b => { if (b) b.classList.remove('active'); });
    const activeBtn = document.getElementById(`sb-mode-${side}-${mode}`);
    if (activeBtn) activeBtn.classList.add('active');

    const fileZone = document.getElementById(`sb-input-${side}-file-zone`);
    const urlZone = document.getElementById(`sb-input-${side}-url-zone`);

    if (fileZone) fileZone.style.display = (mode === 'file') ? 'block' : 'none';
    if (urlZone) urlZone.style.display = (mode === 'url') ? 'block' : 'none';
}

async function handleSandboxFileUpload(side) {
    const input = document.getElementById(`sb-file-${side}-input`);
    if (!input || !input.files || input.files.length === 0) return;

    const file = input.files[0];
    const nameEl = document.getElementById(`sb-file-${side}-name`);
    if (nameEl) {
        nameEl.style.display = 'block';
        nameEl.innerHTML = `⏳ Извлечение текста из <strong>${escapeHtml(file.name)}</strong> (${(file.size / 1024).toFixed(1)} КБ)...`;
    }

    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/sandbox/parse-file', {
            method: 'POST',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            body: formData
        });

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Не удалось распарсить файл');
        }

        const data = await response.json();
        const textarea = document.getElementById(`sandbox-${side}-text`);
        if (textarea) {
            textarea.value = data.text;
            updateSandboxCharCounters(side);
        }

        const formatLabel = document.getElementById(`sb-format-${side}-label`);
        if (formatLabel) {
            formatLabel.innerText = `Файл: ${data.filename} (${data.lines} строк)`;
        }

        if (nameEl) {
            nameEl.innerHTML = `✅ Успешно загружен: <strong>${escapeHtml(data.filename)}</strong> (${data.chars} симв., ${data.words} слов)`;
        }

        showToast(`Файл "${file.name}" успешно преобразован в структурированный текст!`, 'success');
    } catch (e) {
        if (nameEl) nameEl.innerHTML = `<span style="color: var(--danger);">Ошибка: ${escapeHtml(e.message)}</span>`;
        showToast(`Ошибка обработки файла: ${e.message}`, 'error');
    }
}

async function handleSandboxUrlFetch(side) {
    const input = document.getElementById(`sb-url-${side}-input`);
    const url = input?.value.trim();
    if (!url) {
        showToast('Укажите корректный URL адрес или путь к файлу!', 'warning');
        return;
    }

    showToast(`Загрузка документа по ссылке: ${url}...`, 'info');
    const res = await apiRequest('/api/sandbox/fetch-url', 'POST', { url });
    if (res) {
        const textarea = document.getElementById(`sandbox-${side}-text`);
        if (textarea) {
            textarea.value = res.text;
            updateSandboxCharCounters(side);
        }

        const formatLabel = document.getElementById(`sb-format-${side}-label`);
        if (formatLabel) {
            formatLabel.innerText = `Web: ${res.url.substring(0, 30)}... (${res.lines} строк)`;
        }

        showToast(`Документ по ссылке успешно загружен (${res.chars} симв.)`, 'success');
    }
}

function loadSandboxExample() {
    const oldExample = `# Закон Республики Казахстан "О страховой деятельности"

Статья 10. Требования к уставному капиталу страховой (перестраховочной) организации.
1. Минимальный размер уставного капитала создаваемой страховой организации составляет 1 000 000 000 (один миллиард) тенге.
2. Норматив достаточности маржи платежеспособности составляет 1.0 (100%).
3. Настоящие требования действуют до 1 января 2026 года.`;

    const newExample = `# Закон Республики Казахстан "О страховой деятельности"

Статья 10. Требования к уставному капиталу страховой (перестраховочной) организации.
1. Минимальный размер уставного капитала создаваемой страховой организации составляет 1 500 000 000 (один миллиард пятьсот миллионов) тенге.
2. Норматив достаточности маржи платежеспособности страховой организации повышается до 1.2 (120%).
3. Страховые организации обязаны привести размер собственного капитала в соответствие с настоящим пунктом в срок до 1 октября 2026 года.`;

    const oldEl = document.getElementById('sandbox-old-text');
    const newEl = document.getElementById('sandbox-new-text');
    if (oldEl) {
        oldEl.value = oldExample;
        updateSandboxCharCounters('old');
    }
    if (newEl) {
        newEl.value = newExample;
        updateSandboxCharCounters('new');
    }
    showToast('Реальный пример изменения законодательства РК загружен в песочницу', 'success');
}

function clearSandbox() {
    const oldEl = document.getElementById('sandbox-old-text');
    const newEl = document.getElementById('sandbox-new-text');
    if (oldEl) { oldEl.value = ''; updateSandboxCharCounters('old'); }
    if (newEl) { newEl.value = ''; updateSandboxCharCounters('new'); }
    document.getElementById('sandbox-results').style.display = 'none';
    document.getElementById('sandbox-ai-box').style.display = 'none';
    const oldName = document.getElementById('sb-file-old-name');
    const newName = document.getElementById('sb-file-new-name');
    if (oldName) oldName.style.display = 'none';
    if (newName) newName.style.display = 'none';
}

function toggleSandboxDiffFocus() {
    const container = document.getElementById('sandbox-diff-output');
    const btn = document.getElementById('sb-btn-diff-focus');
    if (!container || !btn) return;

    container.classList.toggle('focus-changes');
    const isFocus = container.classList.contains('focus-changes');
    btn.innerText = isFocus ? '📄 Показать весь документ' : '🔍 Только изменения';
    btn.classList.toggle('btn-primary', isFocus);
    btn.classList.toggle('btn-secondary', !isFocus);
}

async function runSandboxCompare() {
    const oldText = document.getElementById('sandbox-old-text').value;
    const newText = document.getElementById('sandbox-new-text').value;

    if (!oldText && !newText) {
        showToast('Введите текст для сравнения или загрузите файл/ссылку', 'warning');
        return;
    }

    const res = await apiRequest('/api/sandbox/compare', 'POST', {
        old_text: oldText,
        new_text: newText
    });

    if (!res) return;

    // Show results container
    const resultsBox = document.getElementById('sandbox-results');
    resultsBox.style.display = 'block';

    // 1. Hash Metric
    const hashStatus = document.getElementById('sb-metric-hash-status');
    const hashVal = document.getElementById('sb-metric-hash-val');
    if (res.is_identical) {
        hashStatus.innerHTML = '<span style="color: #34d399;">Идентичны ✅</span>';
        hashVal.innerText = `SHA: ${res.sha256_old.substring(0, 16)}...`;
    } else {
        hashStatus.innerHTML = '<span style="color: #38bdf8;">Изменен 🔄</span>';
        hashVal.innerText = `v1: ${res.sha256_old.substring(0, 8)}... → v2: ${res.sha256_new.substring(0, 8)}...`;
    }

    // 2. Cosmetic Filter Metric
    const cosmStatus = document.getElementById('sb-metric-cosmetic-status');
    const cosmDesc = document.getElementById('sb-metric-cosmetic-desc');
    if (res.has_real_changes) {
        cosmStatus.innerHTML = '<span style="color: #fb7185;">Существенные правки ⚠️</span>';
        cosmDesc.innerText = 'Затрагивает правовые нормы';
    } else if (res.is_identical) {
        cosmStatus.innerHTML = '<span style="color: #34d399;">Нет изменений</span>';
        cosmDesc.innerText = 'Тексты полностью совпадают';
    } else {
        cosmStatus.innerHTML = '<span style="color: #fbbf24;">Только косметика ℹ️</span>';
        cosmDesc.innerText = 'Изменились только даты/подписи';
    }

    // 3. Characters Metric
    document.getElementById('sb-metric-chars-val').innerText = `${res.chars_new} симв.`;
    const deltaSign = res.chars_delta >= 0 ? `+${res.chars_delta}` : `${res.chars_delta}`;
    document.getElementById('sb-metric-chars-delta').innerText = `Было: ${res.chars_old} (дельта: ${deltaSign})`;

    // 4. Words & Lines Metric
    document.getElementById('sb-metric-words-val').innerText = `${res.words_new} слов`;
    document.getElementById('sb-metric-lines-val').innerText = `Строк: ${res.lines_new} (было: ${res.lines_old})`;

    // 5. Diff Table
    document.getElementById('sandbox-diff-output').innerHTML = res.diff_html;

    showToast('Параметры рассчитаны, Side-by-Side Diff сформирован', 'success');
}

async function runSandboxAIAnalyze() {
    const oldText = document.getElementById('sandbox-old-text').value;
    const newText = document.getElementById('sandbox-new-text').value;

    if (!oldText || !newText) {
        showToast('Заполните обе редакции для анализа нейросетью!', 'warning');
        return;
    }

    const btn = document.getElementById('sandbox-btn-ai');
    const originalText = btn.innerText;
    btn.innerText = '⏳ Gemini анализирует изменения...';
    btn.disabled = true;

    const res = await apiRequest('/api/sandbox/analyze', 'POST', {
        old_text: oldText,
        new_text: newText
    });

    btn.innerText = originalText;
    btn.disabled = false;

    if (!res) return;

    const aiBox = document.getElementById('sandbox-ai-box');
    const aiOutput = document.getElementById('sandbox-ai-output');
    aiBox.style.display = 'block';

    const a = res.analysis || {};
    aiOutput.innerHTML = `
        <div style="margin-bottom: 14px;">
            <div style="font-weight: 700; color: #38bdf8; margin-bottom: 4px;">🔍 Что конкретно изменилось (what_changed):</div>
            <div style="color: var(--text-primary); background: var(--bg-input); padding: 10px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">${escapeHtml(a.what_changed || '—')}</div>
        </div>
        <div style="margin-bottom: 14px;">
            <div style="font-weight: 700; color: #34d399; margin-bottom: 4px;">📋 Новые регуляторные требования (requirements):</div>
            <div style="color: var(--text-primary); background: var(--bg-input); padding: 10px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">${escapeHtml(a.requirements || '—')}</div>
        </div>
        <div style="margin-bottom: 14px;">
            <div style="font-weight: 700; color: #fbbf24; margin-bottom: 4px;">⏰ Сроки и дедлайны (deadlines):</div>
            <div style="color: var(--text-primary); background: var(--bg-input); padding: 10px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">${escapeHtml(a.deadlines || '—')}</div>
        </div>
        <div style="margin-bottom: 14px;">
            <div style="font-weight: 700; color: #fb7185; margin-bottom: 4px;">⚠️ Риски несоблюдения для страховой компании (risks):</div>
            <div style="color: var(--text-primary); background: var(--bg-input); padding: 10px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">${escapeHtml(a.risks || '—')}</div>
        </div>
        <div>
            <div style="font-weight: 700; color: #c084fc; margin-bottom: 4px;">💼 Последствия для бизнес-процессов (consequences):</div>
            <div style="color: var(--text-primary); background: var(--bg-input); padding: 10px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">${escapeHtml(a.consequences || '—')}</div>
        </div>
    `;

    showToast('Юридический анализ успешно сформирован нейросетью!', 'success');
}

function copySandboxAIReport() {
    const output = document.getElementById('sandbox-ai-output');
    if (!output || !output.innerText.trim()) {
        showToast('Отчет еще не сформирован', 'warning');
        return;
    }
    const btn = document.activeElement;
    navigator.clipboard.writeText(output.innerText).then(() => {
        if (btn && btn.tagName === 'BUTTON') {
            const old = btn.innerText;
            btn.classList.add('copied');
            btn.innerText = '✓ Скопировано';
            setTimeout(() => {
                btn.classList.remove('copied');
                btn.innerText = old;
            }, 2000);
        }
        showToast('Юридический отчет скопирован в буфер обмена 📋', 'success');
    }).catch(() => {
        showToast('Не удалось скопировать', 'error');
    });
}

// ----------------- COMMAND PALETTE (Ctrl+K) -----------------

let commandPaletteSelectedIndex = 0;

function openCommandPalette() {
    const modal = document.getElementById('command-palette-modal');
    const input = document.getElementById('command-palette-input');
    if (!modal || !input) return;

    modal.classList.add('active');
    input.value = '';
    input.focus();
    renderCommandPaletteItems('');
}

function closeCommandPalette() {
    const modal = document.getElementById('command-palette-modal');
    if (modal) modal.classList.remove('active');
}

function handleCommandPaletteInput(e) {
    const query = e.target.value.trim().toLowerCase();
    renderCommandPaletteItems(query);
}

function handleCommandPaletteKeydown(e) {
    const results = document.querySelectorAll('.command-item');
    if (results.length === 0) return;

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        commandPaletteSelectedIndex = (commandPaletteSelectedIndex + 1) % results.length;
        updateCommandSelection(results);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        commandPaletteSelectedIndex = (commandPaletteSelectedIndex - 1 + results.length) % results.length;
        updateCommandSelection(results);
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (results[commandPaletteSelectedIndex]) {
            results[commandPaletteSelectedIndex].click();
        }
    }
}

function updateCommandSelection(results) {
    results.forEach((el, idx) => {
        el.classList.toggle('selected', idx === commandPaletteSelectedIndex);
        if (idx === commandPaletteSelectedIndex) {
            el.scrollIntoView({ block: 'nearest' });
        }
    });
}

function renderCommandPaletteItems(query) {
    const box = document.getElementById('command-palette-results');
    if (!box) return;
    box.innerHTML = '';

    const defaultCommands = [
        { icon: getSvgIcon('search', 16), title: 'Мониторинг нормативно-правовых актов', cat: 'Навигация', action: () => switchTab('monitoring') },
        { icon: getSvgIcon('tasks', 16), title: 'Сравнение редакций (Diff Inspector)', cat: 'Навигация', action: () => switchTab('tasks') },
        { icon: getSvgIcon('sandbox', 16), title: 'Быстрое сравнение документов', cat: 'Навигация', action: () => switchTab('sandbox') },
        { icon: getSvgIcon('documents', 16), title: 'Внутренние регламенты компании', cat: 'Навигация', action: () => switchTab('documents') },
        { icon: getSvgIcon('plus', 16), title: 'Добавить закон в мониторинг', cat: 'Действие', action: () => { switchTab('monitoring'); openAddSourceModal(); } },
        { icon: getSvgIcon('upload', 16), title: 'Загрузить регламент (PDF / Word)', cat: 'Действие', action: () => { switchTab('documents'); openAddDocModal(); } },
        { icon: getSvgIcon('refresh', 16), title: 'Запустить опрос по всем законам', cat: 'Действие', action: () => triggerAllChecks() },
        { icon: getSvgIcon('telegram', 16), title: 'Проверить интеграцию с Telegram', cat: 'Интеграция', action: () => sendTelegramTestNotification() },
        { icon: getSvgIcon('trash', 16), title: 'Очистить лабораторию сравнения', cat: 'Лаборатория', action: () => { switchTab('sandbox'); clearSandbox(); } }
    ];

    const filtered = defaultCommands.filter(c => 
        !query || c.title.toLowerCase().includes(query) || c.cat.toLowerCase().includes(query)
    );

    if (filtered.length === 0) {
        box.innerHTML = '<div style="padding: 16px; text-align: center; color: var(--text-muted); font-size: 13px;">Ничего не найдено</div>';
        return;
    }

    commandPaletteSelectedIndex = 0;
    filtered.forEach((cmd, idx) => {
        const item = document.createElement('div');
        item.className = `command-item ${idx === 0 ? 'selected' : ''}`;
        item.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span>${cmd.icon}</span>
                <span style="font-weight: 500;">${escapeHtml(cmd.title)}</span>
            </div>
            <span class="command-item-badge">${escapeHtml(cmd.cat)}</span>
        `;
        item.onclick = () => {
            closeCommandPalette();
            cmd.action();
        };
        box.appendChild(item);
    });
}

// ----------------- SLIDE-OVER DRAWER INSPECTOR -----------------

function openDrawer(title, subtitle, icon, htmlContent) {
    const drawer = document.getElementById('slide-drawer');
    const overlay = document.getElementById('drawer-overlay');
    if (!drawer || !overlay) return;

    document.getElementById('drawer-title').innerText = title || 'Инспектор';
    document.getElementById('drawer-subtitle').innerText = subtitle || '';
    document.getElementById('drawer-icon').innerText = icon || '📄';
    document.getElementById('drawer-body').innerHTML = htmlContent || '';

    overlay.classList.add('active');
    drawer.classList.add('active');
}

function closeDrawer() {
    const drawer = document.getElementById('slide-drawer');
    const overlay = document.getElementById('drawer-overlay');
    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
}

async function inspectRegulationInDrawer(id) {
    const data = await apiRequest('/api/documents');
    if (!data) return;
    const doc = data.find(d => d.id === id);
    if (!doc) return;

    const contentPreview = doc.content_markdown || 'Текст документа пуст.';
    const html = `
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <span class="badge badge-info">${escapeHtml(doc.category)}</span>
            <span class="badge badge-pending">ID: #${doc.id}</span>
        </div>

        <div class="panel" style="background: var(--bg-input); padding: 14px; margin-top: 10px;">
            <div style="font-weight: 600; font-size: 13px; margin-bottom: 6px;">📄 Текст регламента:</div>
            <pre style="white-space: pre-wrap; font-family: var(--font-code); font-size: 12px; color: var(--text-primary); max-height: 340px; overflow-y: auto; background: transparent; border: none; padding: 0;">${escapeHtml(contentPreview)}</pre>
        </div>

        <div style="display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap;">
            <button class="btn btn-secondary btn-sm" onclick="exportInternalDocDocx(${doc.id});">📥 Скачать в Word (.docx)</button>
            <button class="btn btn-primary btn-sm" onclick="closeDrawer(); suggestSourcesForDocument(${doc.id});">📜 Найти законы для регламента</button>
            <button class="btn btn-danger btn-sm" onclick="closeDrawer(); deleteDocument(${doc.id});">🗑️ Удалить</button>
        </div>
    `;

    openDrawer(doc.title, `Категория: ${doc.category}`, '📂', html);
}



