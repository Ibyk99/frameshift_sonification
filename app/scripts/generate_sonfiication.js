


document.getElementById('sonifyBtn').addEventListener('click', async () => {
    const btn = document.getElementById('sonifyBtn');
    btn.disabled = true;
    btn.textContent = 'Generating...';
    

    try {
        const response = await fetch('/alignment/sonify', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: new URLSearchParams({
                'query_seq': '{{ alignment.query }}',
                'subject_seq': '{{ alignment.subject }}'
            })
        });
        
        if (response.ok) {
            document.getElementById('message').innerHTML = 
                '<p style="color: green; background: #d4edda; padding: 12px; border-radius: 4px;">✓ MIDI file generated successfully!</p>';
        } else {
            document.getElementById('message').innerHTML = 
                '<p style="color: red; background: #f8d7da; padding: 12px; border-radius: 4px;">✗ Error generating MIDI</p>';
        }
    } catch (error) {
        document.getElementById('message').innerHTML = 
            '<p style="color: red;">Error: ' + error.message + '</p>';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Generate Sonification';
    }
});

try {
    const son_response = await fetch('/alignment/sonify', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({
                'query_seq': '{{ alignment.query }}',
                'subject_seq': '{{ alignment.subject }}'
            })
        });
        
    } catch (error) {
        document.getElementById('message').innerHTML = 
            '<p style="color: red;">Error: ' + error.message + '</p>';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Generate Sonification';
    }
