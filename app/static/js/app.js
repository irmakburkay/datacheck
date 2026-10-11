document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyzeForm');
    const resultDiv = document.getElementById('result');
    const resultContent = document.getElementById('resultContent');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                resultContent.textContent = JSON.stringify(data, null, 2);
                resultDiv.classList.remove('hidden');
            } else {
                resultContent.textContent = `Error: ${data.error || 'Unknown error'}`;
                resultDiv.classList.remove('hidden');
            }
        } catch (error) {
            resultContent.textContent = `Network error: ${error.message}`;
            resultDiv.classList.remove('hidden');
        }
    });
});
