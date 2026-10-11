document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyzeForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultDiv = document.getElementById('result');
    const resultContent = document.getElementById('resultContent');
    const downloadBtn = document.getElementById('downloadBtn');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Show submitting state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Analyzing…';
        resultDiv.classList.add('hidden');
        downloadBtn.classList.add('hidden');

        const formData = new FormData(form);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                // Format the result for display
                let displayText = `Request ID: ${data.request_id}\nStatus: ${data.status}\n\n`;
                displayText += `Analysis Results:\n`;
                displayText += `  Filename: ${data.analysis.filename}\n`;
                displayText += `  Total Rows: ${data.analysis.total_rows}\n`;
                displayText += `  Total Columns: ${data.analysis.total_columns}\n`;
                displayText += `  Duplicate Rows: ${data.analysis.duplicate_rows}\n`;
                displayText += `  Columns:\n`;
                data.analysis.columns.forEach(col => {
                    displayText += `    - ${col.name}: ${col.data_type} (${col.missing_count} missing, ${col.missing_percentage}%)\n`;
                });
                displayText += `\nDownload URL: ${data.download_url}`;

                resultContent.textContent = displayText;
                resultDiv.classList.remove('hidden');

                // Show download button
                downloadBtn.textContent = `Download Report (${data.analysis.filename})`;
                downloadBtn.onclick = () => {
                    window.location.href = data.download_url;
                };
                downloadBtn.classList.remove('hidden');
            } else {
                resultContent.textContent = `Error: ${data.error || 'Unknown error'}`;
                resultDiv.classList.remove('hidden');
            }
        } catch (error) {
            resultContent.textContent = `Network error: ${error.message}`;
            resultDiv.classList.remove('hidden');
        } finally {
            // Restore button state
            submitBtn.disabled = false;
            submitBtn.textContent = 'Analyze CSV';
        }
    });
});
