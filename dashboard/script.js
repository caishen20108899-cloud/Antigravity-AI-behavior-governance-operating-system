let currentHash = { agents: "", skills: "", issues: "", events: "", digest: "", learning: "" };

function fetchData() {
    // Fetch Agents Data
    fetch('/api/agents')
        .then(response => response.json())
        .then(data => {
            const dataStr = JSON.stringify(data);
            if (currentHash.agents === dataStr) return;
            currentHash.agents = dataStr;

            const container = document.getElementById('agents-container');
            container.innerHTML = '';
            
            if (data.length === 0) {
                container.innerHTML = '<div class="loading">暂无部署特种智能体。</div>';
            } else {
                data.forEach(agent => {
                    const el = document.createElement('div');
                    el.className = 'agent-item';
                    const isActive = agent.status.includes('攻坚');
                    if (isActive) el.classList.add('agent-active');
                    el.innerHTML = `
                        <div>
                            <div class="agent-role">@${agent.role.toUpperCase()}</div>
                            <div class="agent-project">${agent.project || '全局'}</div>
                        </div>
                        <div class="agent-status">${agent.status}</div>
                    `;
                    container.appendChild(el);
                });
            }
        })
        .catch(err => console.error("Error fetching agents:", err));

    // Fetch Skills Data
    fetch('/api/skills')
        .then(response => response.json())
        .then(data => {
            const dataStr = JSON.stringify(data);
            if (currentHash.skills === dataStr) return;
            currentHash.skills = dataStr;

            const container = document.getElementById('skills-container');
            container.innerHTML = '';

            if (data.length === 0) {
                container.innerHTML = '<div class="loading">全局技能矩阵为空。</div>';
            } else {
                data.forEach(skill => {
                    const el = document.createElement('div');
                    el.className = 'skill-tag';
                    el.innerHTML = `
                        <div class="skill-name">${skill.name}</div>
                        <div class="skill-desc">${skill.description}</div>
                    `;
                    container.appendChild(el);
                });
            }
        })
        .catch(err => console.error("Error fetching skills:", err));

    // Fetch Issues Data (Kanban Mode)
    fetch('/api/issues')
        .then(response => response.json())
        .then(data => {
            const dataStr = JSON.stringify(data);
            if (currentHash.issues === dataStr) return;
            currentHash.issues = dataStr;

            const kbPending = document.getElementById('kb-pending');
            const kbProgress = document.getElementById('kb-in-progress');
            const kbBlocker = document.getElementById('kb-blocker');
            const kbDone = document.getElementById('kb-done');

            [kbPending, kbProgress, kbBlocker, kbDone].forEach(el => el.innerHTML = '');
            let counts = { pending: 0, progress: 0, blocker: 0, done: 0 };

            data.forEach(issue => {
                const el = document.createElement('div');
                el.className = 'kb-card';
                let rawText = issue.content;
                let col = kbPending;
                let typeColor = '#94a3b8';

                if (rawText.includes('[In-Progress]')) {
                    col = kbProgress;
                    counts.progress++;
                    typeColor = '#3b82f6';
                } else if (rawText.includes('[Done]')) {
                    col = kbDone;
                    counts.done++;
                    typeColor = '#10b981';
                } else if (rawText.includes('[Blocker]') || rawText.includes('状态: [Blocker]')) {
                    col = kbBlocker;
                    counts.blocker++;
                    typeColor = '#ff4a4a';
                    el.classList.add('blocker-alert');
                } else {
                    counts.pending++;
                }

                let assignee = "@系统";
                const assignMatch = rawText.match(/指派:\s*\[(@[^\]]+)\]/);
                if (assignMatch) assignee = assignMatch[1];
                
                let issueId = "Task";
                const idMatch = rawText.match(/\[Issue-([^\]]+)\]/);
                if (idMatch) issueId = idMatch[1];

                el.innerHTML = `
                    <div class="kb-card-indicator" style="background-color: ${typeColor};"></div>
                    <div class="kb-project">${issue.project} - ${issueId}</div>
                    <div class="kb-title">${rawText}</div>
                    <div class="kb-avatar">🧑‍💻 <span style="color:${typeColor}">${assignee}</span></div>
                `;
                col.appendChild(el);
            });

            document.getElementById('count-pending').textContent = counts.pending;
            document.getElementById('count-in-progress').textContent = counts.progress;
            document.getElementById('count-blocker').textContent = counts.blocker;
            document.getElementById('count-done').textContent = counts.done;
        })
        .catch(err => console.error("Error fetching issues:", err));

    // Fetch Event Logs (Live Terminal)
    fetch('/api/events')
        .then(response => response.json())
        .then(data => {
            const dataStr = JSON.stringify(data);
            if (currentHash.events === dataStr) return;
            currentHash.events = dataStr;

            const terminal = document.getElementById('terminal-stream');
            terminal.innerHTML = '';
            
            if (data.length === 0) {
                terminal.innerHTML = '<div class="terminal-line"><span class="t-time">['+new Date().toLocaleTimeString()+']</span> <span class="t-agent">@系统</span> <span class="t-msg">监听端口已连接，等待截获中...</span></div>';
            } else {
                data.forEach(evt => {
                    const timeStr = new Date(evt.timestamp * 1000).toLocaleTimeString();
                    let cssClass = "";
                    let prefix = "";
                    if (evt.type === 'MessageThinking') { cssClass = 'evt-thinking'; prefix = '[🧠 思考推演] '; }
                    else if (evt.type === 'MessageToolUse') { cssClass = 'evt-tooluse'; prefix = `[⚙️ 发起调用: ${evt.tool}] `; }
                    else if (evt.type === 'MessageToolResult') { cssClass = 'evt-toolresult'; prefix = '[✅ 执行完毕] '; }
                    else if (evt.type === 'MessageStatus') { cssClass = 'evt-status'; prefix = '[📡 阵列指令] '; }
                    else if (evt.type === 'MessageError') { cssClass = 'evt-error'; prefix = '[❌ 异常拦截] '; }
                    else { cssClass = 'evt-log'; prefix = '[📝 日志] '; }

                    const el = document.createElement('div');
                    el.className = 'terminal-line';
                    el.innerHTML = `<span class="t-time">[${timeStr}]</span> <span class="t-agent">${evt.agent}</span> <span class="${cssClass}">${prefix}${evt.content}</span>`;
                    terminal.appendChild(el);
                });
                terminal.scrollTop = terminal.scrollHeight;
            }
        })
        .catch(err => console.error("Error fetching events:", err));

    // Fetch Community Digest
    fetch('/api/digest')
        .then(response => response.json())
        .then(data => {
            const dataStr = JSON.stringify(data);
            if (currentHash.digest === dataStr) return;
            currentHash.digest = dataStr;

            const container = document.getElementById('digest-container');
            const dateEl = document.getElementById('digest-date');

            if (!data.raw_exists) {
                container.innerHTML = '<div class="loading">📡 暂无社区简报数据。请先运行 ag_evolve.py 生成简报。</div>';
                return;
            }

            let dateText = data.date ? `📅 ${data.date}` : '';
            if (data.is_stale) {
                dateText += ` <span class="stale-badge">⚠️ ${Math.round(data.age_hours)}h ago · 需运行 ag_evolve 刷新</span>`;
            }
            dateEl.innerHTML = dateText;

            let html = '<div class="digest-grid">';

            // GitHub Trending
            html += '<div class="digest-section">';
            html += '<div class="digest-section-title"><span class="digest-icon gh-icon">🔥</span> GitHub 热门</div>';
            if (data.github && data.github.length > 0) {
                data.github.forEach(repo => {
                    const langBadge = repo.lang ? `<span class="digest-lang">${repo.lang}</span>` : '';
                    html += `
                        <a href="${repo.url}" target="_blank" class="digest-item gh-item">
                            <div class="digest-item-top">
                                <span class="digest-repo-name">${repo.name}</span>
                                <span class="digest-stars">⭐ ${repo.stars}</span>
                            </div>
                            <div class="digest-item-desc">${repo.desc}</div>
                            ${langBadge}
                        </a>
                    `;
                });
            } else {
                html += '<div class="digest-empty">数据暂不可用</div>';
            }
            html += '</div>';

            // Hacker News
            html += '<div class="digest-section">';
            html += '<div class="digest-section-title"><span class="digest-icon hn-icon">📰</span> Hacker News</div>';
            if (data.hackernews && data.hackernews.length > 0) {
                data.hackernews.forEach(item => {
                    html += `
                        <a href="${item.url}" target="_blank" class="digest-item hn-item">
                            <div class="digest-item-title">${item.title}</div>
                            <div class="digest-item-meta">
                                <span>△${item.score}</span>
                                <span>💬${item.comments}</span>
                                ${item.hn_url ? `<a href="${item.hn_url}" target="_blank" class="hn-discuss">讨论</a>` : ''}
                            </div>
                        </a>
                    `;
                });
            } else {
                html += '<div class="digest-empty">今日无匹配新闻</div>';
            }
            html += '</div>';

            // Awesome
            html += '<div class="digest-section">';
            html += '<div class="digest-section-title"><span class="digest-icon aw-icon">📚</span> Awesome 动态</div>';
            if (data.awesome && data.awesome.length > 0) {
                data.awesome.forEach(item => {
                    html += `
                        <div class="digest-item aw-item">
                            <div class="digest-aw-repo">${item.repo}</div>
                            <div class="digest-item-desc">${item.message}</div>
                            <div class="digest-aw-date">${item.date}</div>
                        </div>
                    `;
                });
            } else {
                html += '<div class="digest-empty">近期无更新</div>';
            }
            html += '</div>';

            // Reddit /r/MachineLearning
            html += '<div class="digest-section">';
            html += '<div class="digest-section-title"><span class="digest-icon" style="color:#ff4500;">🔴</span> Reddit ML</div>';
            if (data.reddit && data.reddit.length > 0) {
                data.reddit.forEach(item => {
                    const flairBadge = item.flair ? `<span class="digest-lang" style="background:rgba(255,69,0,0.15);color:#ff4500;">${item.flair}</span>` : '';
                    html += `
                        <a href="${item.reddit_url || item.url}" target="_blank" class="digest-item">
                            <div class="digest-item-title">${item.title}</div>
                            <div class="digest-item-meta">
                                <span>△${item.score}</span>
                                <span>💬${item.comments}</span>
                            </div>
                            ${flairBadge}
                        </a>
                    `;
                });
            } else {
                html += '<div class="digest-empty">数据暂不可用</div>';
            }
            html += '</div>';

            // arXiv Papers
            html += '<div class="digest-section">';
            html += '<div class="digest-section-title"><span class="digest-icon" style="color:#b31b1b;">📄</span> arXiv 论文</div>';
            if (data.arxiv && data.arxiv.length > 0) {
                data.arxiv.forEach(item => {
                    html += `
                        <a href="${item.url}" target="_blank" class="digest-item">
                            <div class="digest-item-title" style="font-size:0.72rem;">${item.title}</div>
                            <div class="digest-item-desc">${item.summary}</div>
                            <div class="digest-aw-date">${item.date}</div>
                        </a>
                    `;
                });
            } else {
                html += '<div class="digest-empty">数据暂不可用</div>';
            }

            if (data.suggestion) {
                html += `
                    <div class="digest-suggestion">
                        <span class="digest-icon">🎯</span> ${data.suggestion}
                    </div>
                `;
            }
            html += '</div>';
            html += '</div>';
            container.innerHTML = html;
        })
        .catch(err => console.error("Error fetching digest:", err));

    // Fetch AI Learning Digest
    fetch('/api/learning')
        .then(response => response.json())
        .then(data => {
            const dataStr = JSON.stringify(data);
            if (currentHash.learning === dataStr) return;
            currentHash.learning = dataStr;

            const container = document.getElementById('learning-container');
            const dateEl = document.getElementById('learning-date');

            let dateText = data.date ? `📅 ${data.date}` : '';
            if (data.is_stale) {
                dateText += ` <span class="stale-badge">⚠️ ${Math.round(data.age_hours || 0)}h ago · 数据待刷新</span>`;
            }
            dateEl.innerHTML = dateText;

            let html = '<div class="digest-grid" style="grid-template-columns: 1fr 1fr;">';

            // Left: New Skills
            html += '<div class="digest-column">';
            html += '<h3 class="digest-col-title">🃏 新增神经认知 (New Skills)</h3>';
            if (data.new_skills && data.new_skills.length > 0) {
                data.new_skills.forEach(skill => {
                    html += `
                        <div class="digest-item">
                            <div class="digest-title-row">
                                <a href="#" class="digest-title" style="color: var(--color-accent-blue);">@${skill.name}</a>
                            </div>
                            <div class="digest-desc">${skill.desc || '技能参数未解析'}</div>
                        </div>
                    `;
                });
            } else {
                html += '<div class="digest-empty">过去48小时暂无新技能衍生</div>';
            }
            html += '</div>';

            // Right: Memory Sync
            html += '<div class="digest-column">';
            html += '<h3 class="digest-col-title">📂 系统记忆同步 (Memory Sync)</h3>';
            if (data.updated_memories && data.updated_memories.length > 0) {
                data.updated_memories.forEach(mem => {
                    html += `
                        <div class="digest-item">
                            <div class="digest-title-row">
                                <span class="digest-title" style="color: var(--color-success);">${mem.project}</span>
                            </div>
                            <div class="digest-desc" style="opacity: 0.8;">${mem.desc}</div>
                        </div>
                    `;
                });
            } else {
                html += '<div class="digest-empty">过去48小时系统记忆无偏转</div>';
            }
            html += '</div>';

            html += '</div>';
            container.innerHTML = html;
        })
        .catch(err => console.error("Error fetching learning digest:", err));
}

document.addEventListener('DOMContentLoaded', () => {
    fetchData();

    const navItems = document.querySelectorAll('.nav-item');
    const panelSections = document.querySelectorAll('.panel-section');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            panelSections.forEach(panel => { panel.classList.remove('active'); });
            const target = item.getAttribute('data-target');
            document.querySelector(`.${target}`).classList.add('active');
        });
    });

    setInterval(fetchData, 3000);
});
