document.addEventListener('DOMContentLoaded', () => {

  const languageSelect = document.getElementById('languageSelect');
  if (!languageSelect) return; // not on editor page

  const editor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
    mode: languageSelect.value,
    theme: 'material-darker',
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    viewportMargin: Infinity,
  });

  languageSelect.addEventListener('change', () => {
    editor.setOption('mode', languageSelect.value);
    const title = document.querySelector('.pane-title');
    if (title) {
      const ext = { python: 'py', javascript: 'js', htmlmixed: 'html', css: 'css', cpp: 'cpp', java: 'java' };
      title.textContent = 'editor.' + (ext[languageSelect.value] || 'txt');
    }
  });

  /* Tabs */
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('is-active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('is-active'));
      tab.classList.add('is-active');
      document.getElementById(`tab-${tab.dataset.tab}`).classList.add('is-active');
    });
  });

  const footerStatus = document.getElementById('footerStatus');
  const setStatus = (text) => { if (footerStatus) footerStatus.textContent = text; };

  function renderMarkdownish(text) {
    const escape = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const parts = text.split(/```(\w*)\n?([\s\S]*?)```/g);
    let html = '';
    for (let i = 0; i < parts.length; i += 3) {
      const plain = parts[i];
      if (plain && plain.trim()) {
        html += plain.trim().split(/\n{2,}/).map(p => `<p>${escape(p)}</p>`).join('');
      }
      const lang = parts[i + 1];
      const code = parts[i + 2];
      if (code !== undefined) {
        html += `<pre><code class="lang-${escape(lang || '')}">${escape(code.trim())}</code></pre>`;
      }
    }
    return html || `<p>${escape(text)}</p>`;
  }

  const chatLog = document.getElementById('chatLog');

  function addMessage(role, content, { asHtml = false } = {}) {
    const div = document.createElement('div');
    div.className = `msg msg-${role}`;
    if (asHtml) {
      div.innerHTML = content;
    } else {
      const p = document.createElement('p');
      p.textContent = content;
      div.appendChild(p);
    }
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
    return div;
  }

  function addLoading(text) {
    const div = document.createElement('div');
    div.className = 'msg msg-loading';
    div.textContent = text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
    return div;
  }

  /* Assist buttons */
  document.querySelectorAll('.action-btn[data-mode]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const mode = btn.dataset.mode;
      const code = editor.getValue();
      if (!code.trim()) {
        addMessage('error', 'The editor is empty — write or paste some code first.');
        return;
      }
      document.querySelector('.tab[data-tab="chat"]')?.click();
      const label = btn.textContent.trim();
      addMessage('user', `${label} this code`);
      const loading = addLoading('Autocode AI is thinking…');
      btn.disabled = true;
      setStatus(`Running "${label}"…`);
      try {
        const res = await fetch('/api/assist', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mode, code, language: languageSelect.value }),
        });
        const data = await res.json();
        loading.remove();
        if (!res.ok) addMessage('error', data.error || 'Something went wrong.');
        else addMessage('ai', renderMarkdownish(data.reply), { asHtml: true });
      } catch (err) {
        loading.remove();
        addMessage('error', `Request failed: ${err.message}`);
      } finally {
        btn.disabled = false;
        setStatus('Ready');
      }
    });
  });

  /* Run code */
  const runBtn = document.getElementById('runBtn');
  const runOutput = document.getElementById('runOutput');
  const clearOutput = document.getElementById('clearOutput');

  clearOutput?.addEventListener('click', () => {
    runOutput.textContent = '// Output cleared';
  });

  runBtn?.addEventListener('click', async () => {
    const code = editor.getValue();
    if (!code.trim()) {
      runOutput.textContent = 'Error: editor is empty.';
      return;
    }
    runBtn.disabled = true;
    runBtn.textContent = 'Running…';
    runOutput.textContent = 'Executing…';
    setStatus('Running code…');
    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language: languageSelect.value }),
      });
      const data = await res.json();
      if (!res.ok) {
        runOutput.textContent = data.error || 'Run failed';
      } else {
        let out = '';
        if (data.stdout) out += data.stdout;
        if (data.stderr) out += (out ? '\n' : '') + data.stderr;
        if (!out.trim()) out = `(exit ${data.returncode}) — no output`;
        else if (data.returncode !== 0) out += `\n[exit code ${data.returncode}]`;
        runOutput.textContent = out;
      }
    } catch (err) {
      runOutput.textContent = `Request failed: ${err.message}`;
    } finally {
      runBtn.disabled = false;
      runBtn.textContent = '▶ Run';
      setStatus('Ready');
    }
  });

  /* Chat */
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const history = [];

  chatForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;
    addMessage('user', message);
    history.push({ role: 'user', content: message });
    chatInput.value = '';
    const loading = addLoading('Autocode AI is thinking…');
    setStatus('Waiting for Gemini…');
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          history,
          code: editor.getValue(),
          language: languageSelect.value,
        }),
      });
      const data = await res.json();
      loading.remove();
      if (!res.ok) addMessage('error', data.error || 'Something went wrong.');
      else {
        addMessage('ai', renderMarkdownish(data.reply), { asHtml: true });
        history.push({ role: 'assistant', content: data.reply });
      }
    } catch (err) {
      loading.remove();
      addMessage('error', `Request failed: ${err.message}`);
    } finally {
      setStatus('Ready');
    }
  });

  chatInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chatForm.requestSubmit();
    }
  });

  /* Scan */
  const scanDrop = document.getElementById('scanDrop');
  const scanFile = document.getElementById('scanFile');
  const scanBrowse = document.getElementById('scanBrowse');
  const scanDropInner = document.getElementById('scanDropInner');
  const scanStage = document.getElementById('scanStage');
  const scanImg = document.getElementById('scanImg');
  const scanSweep = document.getElementById('scanSweep');
  const scanRunBtn = document.getElementById('scanRunBtn');
  const scanResult = document.getElementById('scanResult');
  const scanText = document.getElementById('scanText');
  const scanInsertBtn = document.getElementById('scanInsertBtn');
  let selectedFile = null;

  function showPreview(file) {
    selectedFile = file;
    const url = URL.createObjectURL(file);
    scanImg.src = url;
    scanDropInner.hidden = true;
    scanStage.hidden = false;
    scanSweep.style.animationPlayState = 'paused';
    scanSweep.style.opacity = '0';
    scanRunBtn.disabled = false;
    scanResult.hidden = true;
  }

  scanBrowse?.addEventListener('click', (e) => { e.stopPropagation(); scanFile.click(); });
  scanDrop?.addEventListener('click', (e) => {
    if (e.target === scanBrowse) return;
    scanFile.click();
  });
  scanFile?.addEventListener('change', () => {
    if (scanFile.files[0]) showPreview(scanFile.files[0]);
  });

  ['dragover', 'dragenter'].forEach(evt =>
    scanDrop?.addEventListener(evt, (e) => { e.preventDefault(); scanDrop.classList.add('is-dragover'); })
  );
  ['dragleave', 'drop'].forEach(evt =>
    scanDrop?.addEventListener(evt, (e) => { e.preventDefault(); scanDrop.classList.remove('is-dragover'); })
  );
  scanDrop?.addEventListener('drop', (e) => {
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) showPreview(file);
  });

  scanRunBtn?.addEventListener('click', async () => {
    if (!selectedFile) return;
    scanRunBtn.disabled = true;
    scanRunBtn.textContent = 'Scanning…';
    scanSweep.style.opacity = '1';
    scanSweep.style.animationPlayState = 'running';
    setStatus('Running OpenCV preprocessing + OCR…');
    const formData = new FormData();
    formData.append('image', selectedFile);
    try {
      const res = await fetch('/api/scan', { method: 'POST', body: formData });
      const data = await res.json();
      if (!res.ok) {
        scanResult.hidden = false;
        scanText.textContent = `Error: ${data.error || 'scan failed'}`;
      } else {
        if (data.preview) scanImg.src = data.preview;
        scanResult.hidden = false;
        scanText.textContent = data.text || '(No text detected — try a clearer, well-lit photo.)';
      }
    } catch (err) {
      scanResult.hidden = false;
      scanText.textContent = `Request failed: ${err.message}`;
    } finally {
      scanSweep.style.animationPlayState = 'paused';
      scanSweep.style.opacity = '0';
      scanRunBtn.disabled = false;
      scanRunBtn.textContent = 'Run OCR scan';
      setStatus('Ready');
    }
  });

  scanInsertBtn?.addEventListener('click', () => {
    const text = scanText.textContent;
    if (!text) return;
    editor.replaceRange(text, editor.getCursor());
    document.querySelector('.tab[data-tab="chat"]')?.click();
    editor.focus();
  });
});
