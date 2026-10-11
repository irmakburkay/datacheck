document.addEventListener('DOMContentLoaded', function () {

    // ── Elements ─────────────────────────────────────────────────────
    const form          = document.getElementById('analyzeForm');
    const submitBtn     = document.getElementById('submitBtn');
    const submitLabel   = document.getElementById('submitLabel');
    const submitSpinner = document.getElementById('submitSpinner');

    const fileZone      = document.getElementById('fileZone');
    const fileInput     = document.getElementById('csv_file');
    const fileZoneLabel = document.getElementById('fileZoneLabel');

    const resultsPlaceholder = document.getElementById('resultsPlaceholder');
    const resultsBody        = document.getElementById('resultsBody');
    const resultsError       = document.getElementById('resultsError');

    // ── File zone ─────────────────────────────────────────────────────
    fileInput.addEventListener('change', () => updateFileLabel(fileInput.files[0]));

    fileZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileZone.classList.add('dragover');
    });
    fileZone.addEventListener('dragleave', () => fileZone.classList.remove('dragover'));
    fileZone.addEventListener('drop', (e) => {
        e.preventDefault();
        fileZone.classList.remove('dragover');
        const file = e.dataTransfer?.files[0];
        if (file) {
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
            updateFileLabel(file);
        }
    });
    fileZone.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); }
    });

    function updateFileLabel(file) {
        if (!file) return;
        fileZoneLabel.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path d="M10 3v10M10 3l-3 3M10 3l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M3 14v1a2 2 0 002 2h10a2 2 0 002-2v-1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <span>${escHtml(file.name)}</span>
            <span class="file-hint">${formatBytes(file.size)}</span>
        `;
        fileZone.classList.add('has-file');
        clearErr('file-err');
    }

    // ── Submit ────────────────────────────────────────────────────────
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!validate()) return;

        setLoading(true);
        showPanel('placeholder');

        try {
            const res  = await fetch('/api/analyze', { method: 'POST', body: new FormData(form) });
            const data = await res.json();
            if (res.ok) {
                renderResults(data);
            } else {
                showPanel('error', data.error || data.message || 'Something went wrong. Please try again.');
            }
        } catch {
            showPanel('error', 'Network error — please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    });

    // ── Validation ────────────────────────────────────────────────────
    function validate() {
        let ok = true;

        const name = form.querySelector('#name').value.trim();
        if (!name) { setErr('name', 'name-err', 'Name is required.'); ok = false; }
        else clearErr('name-err');

        const email = form.querySelector('#email').value.trim();
        if (!email) { setErr('email', 'email-err', 'Email is required.'); ok = false; }
        else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setErr('email', 'email-err', 'Enter a valid email address.'); ok = false; }
        else clearErr('email-err');

        const service = form.querySelector('#service').value;
        if (!service) { setErr('service', 'service-err', 'Please select a service.'); ok = false; }
        else clearErr('service-err');

        if (!fileInput.files || !fileInput.files[0]) {
            document.getElementById('file-err').textContent = 'Please select a CSV file.';
            fileZone.style.borderColor = 'var(--error)';
            ok = false;
        } else {
            clearErr('file-err');
            fileZone.style.borderColor = '';
        }

        return ok;
    }

    function setErr(fieldId, errId, msg) {
        const f = document.getElementById(fieldId);
        const e = document.getElementById(errId);
        if (f) f.classList.add('invalid');
        if (e) e.textContent = msg;
    }
    function clearErr(errId) {
        const e = document.getElementById(errId);
        if (e) e.textContent = '';
        const fieldId = errId.replace('-err', '');
        const f = document.getElementById(fieldId);
        if (f) f.classList.remove('invalid');
    }

    // ── UI state ──────────────────────────────────────────────────────
    function setLoading(on) {
        submitBtn.disabled = on;
        submitLabel.textContent = on ? 'Analyzing…' : 'Analyze CSV';
        submitSpinner.classList.toggle('hidden', !on);
    }

    function showPanel(state, msg) {
        resultsPlaceholder.classList.toggle('hidden', state !== 'placeholder');
        resultsBody.classList.toggle('hidden',        state !== 'results');
        resultsError.classList.toggle('hidden',       state !== 'error');
        if (state === 'error') document.getElementById('errMsg').textContent = msg || '';
    }

    // ── Render results ────────────────────────────────────────────────
    function renderResults(data) {
        const a = data.analysis;

        document.getElementById('resultsFilename').textContent = a.filename;
        document.getElementById('resultsRid').textContent = 'ID ' + data.request_id;
        document.getElementById('mRows').textContent  = a.total_rows.toLocaleString();
        document.getElementById('mCols').textContent  = a.total_columns.toLocaleString();
        document.getElementById('mDupes').textContent = a.duplicate_rows.toLocaleString();

        const tbody = document.getElementById('colBody');
        tbody.innerHTML = '';
        (a.columns || []).forEach(col => {
            const pct = col.missing_percentage;
            let pctClass = 'col-pct';
            if (pct >= 30) pctClass += ' pct-err';
            else if (pct >= 10) pctClass += ' pct-warn';

            const typeClass = {
                integer: 'badge-int',
                float:   'badge-flt',
                string:  'badge-str',
                date:    'badge-dat',
                boolean: 'badge-boo'
            }[col.data_type] || 'badge-str';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${escHtml(col.name)}</td>
                <td><span class="badge ${typeClass}">${escHtml(col.data_type)}</span></td>
                <td>${(col.unique_count || 0).toLocaleString()}</td>
                <td>${col.missing_count.toLocaleString()}</td>
                <td class="${pctClass}">${pct.toFixed(1)}%</td>
            `;
            tbody.appendChild(tr);
            
            // Add stats row if available
            if (col.stats || col.date_range) {
                const detailTr = document.createElement('tr');
                detailTr.className = 'col-detail';
                let detailHtml = '<td colspan="5"><div class="col-stats">';
                
                if (col.stats) {
                    detailHtml += `
                        <span>Min: ${col.stats.min}</span>
                        <span>Max: ${col.stats.max}</span>
                        <span>Mean: ${col.stats.mean}</span>
                        <span>Median: ${col.stats.median}</span>
                    `;
                }
                
                if (col.date_range) {
                    detailHtml += `
                        <span>Earliest: ${col.date_range.earliest}</span>
                        <span>Latest: ${col.date_range.latest}</span>
                    `;
                }
                
                detailHtml += '</div></td>';
                detailTr.innerHTML = detailHtml;
                tbody.appendChild(detailTr);
            }
        });

        document.getElementById('downloadBtn').onclick = () => {
            window.location.href = data.download_url;
        };

        showPanel('results');

        if (window.innerWidth < 820) {
            resultsBody.closest('.results-card')
                .scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    // ── Helpers ───────────────────────────────────────────────────────
    function escHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
    function formatBytes(b) {
        if (b < 1024)       return b + ' B';
        if (b < 1048576)    return (b / 1024).toFixed(1) + ' KB';
        return (b / 1048576).toFixed(1) + ' MB';
    }

});
