document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('aiToggle');
  const box = document.getElementById('aiContainer');
  const body = document.getElementById('aiBody');
  const input = document.getElementById('aiInput');
  const send = document.getElementById('aiSend');
  const close = document.getElementById('aiClose');
  const sugg = document.getElementById('aiSuggestions');
  let typing = false;

  if (!toggle || !box) return;

  toggle.addEventListener('click', () => {
    box.classList.toggle('open');
    if (box.classList.contains('open')) { input.focus(); body.scrollTop = body.scrollHeight; }
  });
  close.addEventListener('click', () => box.classList.remove('open'));

  const add = (text, who) => {
    const m = document.createElement('div');
    m.className = 'ai-msg ' + who;
    const av = document.createElement('div');
    av.className = 'ai-avatar';
    av.innerHTML = who === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    const c = document.createElement('div');
    c.className = 'ai-content';
    c.innerHTML = text.replace(/\n/g, '<br>');
    if (who === 'user') { m.appendChild(c); m.appendChild(av); }
    else { m.appendChild(av); m.appendChild(c); }
    body.appendChild(m);
    body.scrollTop = body.scrollHeight;
  };

  const submit = () => {
    const text = input.value.trim();
    if (!text || typing) return;
    add(text, 'user'); input.value = ''; typing = true;
    fetch('/ai/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, page_url: window.location.pathname })
    })
    .then(r => r.json())
    .then(d => { typing = false; add(d.response, 'bot'); if (d.suggestions) updateSugg(d.suggestions); })
    .catch(() => { typing = false; add('⚠️ Error. Please try again.', 'bot'); });
  };

  const updateSugg = (list) => {
    if (!sugg) return;
    sugg.innerHTML = '';
    list.forEach(s => {
      const b = document.createElement('button');
      b.className = 'ai-suggestion'; b.textContent = s;
      b.addEventListener('click', () => { input.value = s; submit(); });
      sugg.appendChild(b);
    });
  };

  send.addEventListener('click', submit);
  input.addEventListener('keypress', e => { if (e.key === 'Enter') { e.preventDefault(); submit(); }});

  fetch('/ai/suggestions?page=' + encodeURIComponent(window.location.pathname))
    .then(r => r.json()).then(d => { if (d.suggestions) updateSugg(d.suggestions); });
});
