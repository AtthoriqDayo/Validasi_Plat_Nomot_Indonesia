/* --- NAVIGATION SYSTEM --- */
function showSection(id) {
    document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById('section-' + id).classList.add('active');
    
    const map = {'visualizer': 0, 'performance': 1, 'ocr': 2};
    document.querySelectorAll('.nav-item')[map[id]].classList.add('active');
}

/* --- FEATURE 1: DFA VISUALIZER (Adjusted) --- */
async function runVisualizer() {
    const input = document.getElementById('plateInput').value;
    const statusText = document.getElementById('statusText');
    
    if (!input) return;

    // Reset UI
    document.querySelectorAll('.node').forEach(n => {
        n.className = 'node'; // Remove all active/trap classes
    });
    statusText.innerText = "INITIALIZING PROTOCOLS...";
    statusText.style.color = "var(--text-main)";

    try {
        const response = await fetch(`/api/validate-dfa/?plate=${encodeURIComponent(input)}`);
        const data = await response.json();

        // 1. Loop through history
        for (let step of data.history) {
            const nodeId = 'node-' + step.state;
            const nodeEl = document.getElementById(nodeId);
            
            if (nodeEl) {
                // Highlight Logic
                if (step.state === 'TRAP') {
                    nodeEl.classList.add('trap-state');
                    // Show the specific error reason
                    statusText.innerText = `ERROR: ${step.reason}`; 
                    statusText.style.color = "var(--neon-pink)";
                } else {
                    nodeEl.classList.add('active-neon');
                    const char = step.input ? `Processing: '${step.input}'` : 'Start';
                    statusText.innerText = `${char} >> State: ${step.state}`;
                    statusText.style.color = "var(--text-main)";
                }

                // 2. SLOW DOWN: Increased from 500ms to 1200ms
                await new Promise(r => setTimeout(r, 1200));
                
                // Remove highlight if not trapped
                if (step.state !== 'TRAP') {
                    nodeEl.classList.remove('active-neon');
                }
            }
        }

        // Final Verification
        if (data.is_valid) {
            statusText.innerText = "ACCESS GRANTED: VALID PLATE";
            statusText.style.color = "var(--neon-green)";
        } else if (!data.is_valid && data.history[data.history.length-1].state !== 'TRAP') {
            // Case where input ran out but wasn't in a final state
            statusText.innerText = "INCOMPLETE INPUT";
            statusText.style.color = "var(--neon-pink)";
        }

    } catch (e) {
        console.error(e);
        statusText.innerText = "SYSTEM ERROR";
    }
}

/* --- GLOBAL VARIABLES --- */
let inputChips = []; // Stores the manual plates

/* --- CHIP INPUT LOGIC --- */
// Attach this event listener when page loads
document.addEventListener('DOMContentLoaded', () => {
    const typer = document.getElementById('plate-typer');
    
    if(typer) {
        typer.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const val = this.value.trim().toUpperCase();
                if (val) {
                    addChip(val);
                    this.value = '';
                }
            } else if (e.key === 'Backspace' && this.value === '') {
                // Remove last chip
                if (inputChips.length > 0) {
                    inputChips.pop();
                    renderChips();
                }
            }
        });
    }
});

function addChip(text) {
    if (!inputChips.includes(text)) {
        inputChips.push(text);
        renderChips();
    }
}

function removeChip(index) {
    inputChips.splice(index, 1);
    renderChips();
}

function renderChips() {
    const container = document.querySelector('.chip-container');
    const typer = document.getElementById('plate-typer');
    
    // Clear old chips (keep the input at the end)
    const existingChips = container.querySelectorAll('.chip');
    existingChips.forEach(c => c.remove());

    // Add new chips before the input
    inputChips.forEach((text, index) => {
        const chip = document.createElement('div');
        chip.className = 'chip';
        chip.innerHTML = `${text} <span onclick="removeChip(${index})">×</span>`;
        container.insertBefore(chip, typer);
    });
}

/* --- BENCHMARK LOGIC (UPDATED) --- */
async function runBenchmark() {
    const btn = document.getElementById('btn-benchmark');
    const resultArea = document.getElementById('benchmark-result');
    const logBox = document.getElementById('detailed-log');
    const timerDisplay = document.getElementById('progress-timer');
    const showDetails = document.getElementById('show-details').checked;
    
    // 1. Prepare Payload
    let finalPayload = [...inputChips]; // Start with chips
    
    // Multiplier
    const multiplier = parseInt(document.getElementById('bench-multiplier').value) || 1;
    let baseList = [...finalPayload];
    finalPayload = [];
    for(let i=0; i<multiplier; i++) finalPayload = finalPayload.concat(baseList);

    // CSV
    const fileInput = document.getElementById('bench-csv');
    if (fileInput.files.length > 0) {
        try {
            const text = await fileInput.files[0].text();
            const csvPlates = text.split(/[\r\n,]+/).map(s => s.trim()).filter(s => s);
            finalPayload = finalPayload.concat(csvPlates);
        } catch(e) { alert("CSV Error"); return; }
    }

    if (finalPayload.length === 0) { alert("Please type a plate and hit Enter!"); return; }

    // 2. Start UI "Processing" State
    btn.disabled = true;
    logBox.style.display = 'none'; // Hide old logs
    resultArea.innerHTML = "";
    
    let startTime = Date.now();
    // Start "Alive" Timer
    const timerInterval = setInterval(() => {
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        timerDisplay.innerText = `SYSTEM PROCESSING... [ TIME ELAPSED: ${elapsed}s ]`;
    }, 100);

    try {
        const response = await fetch('/api/compare-speed/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                plates: finalPayload,
                include_details: showDetails // Tell backend if we want the list
            })
        });
        
        const data = await response.json();
        
        // Stop Timer
        clearInterval(timerInterval);
        timerDisplay.innerText = "PROCESS COMPLETE.";

        // 3. Render Stats
        const max = Math.max(data.dfa_duration_ms, data.db_duration_ms);
        document.getElementById('bar-dfa').style.width = (data.dfa_duration_ms / max * 100) + "%";
        document.getElementById('bar-dfa').innerText = data.dfa_duration_ms + " ms";
        document.getElementById('bar-db').style.width = (data.db_duration_ms / max * 100) + "%";
        document.getElementById('bar-db').innerText = data.db_duration_ms + " ms";
        
        resultArea.innerHTML = `
            <h3 style="color: var(--neon-cyan)">WINNER: ${data.winner}</h3>
            <p>Analyzed <strong>${data.count.toLocaleString()}</strong> items.</p>
        `;

        // 4. Render Detailed Log (If requested)
        if (showDetails && data.details) {
            logBox.style.display = 'block';
            logBox.innerHTML = ""; // Clear
            
            // Limit display to 1000 items to prevent browser crash
            const limit = Math.min(data.details.length, 1000);
            
            data.details.slice(0, limit).forEach(item => {
                const row = document.createElement('div');
                row.className = 'log-item';
                const statusClass = item.is_valid ? 'log-valid' : 'log-invalid';
                const statusText = item.is_valid ? 'VALID' : 'INVALID';
                
                row.innerHTML = `
                    <span>${item.plate}</span>
                    <span class="${statusClass}">[${statusText}] ${item.reason || ''}</span>
                `;
                logBox.appendChild(row);
            });

            if (data.details.length > 1000) {
                const note = document.createElement('div');
                note.style.padding = "10px";
                note.style.color = "#888";
                note.innerText = `... and ${data.details.length - 1000} more items (hidden for performance).`;
                logBox.appendChild(note);
            }
        }

    } catch (e) {
        clearInterval(timerInterval);
        timerDisplay.innerText = "SYSTEM FAILURE";
        resultArea.innerHTML = `<span style="color:red">Error: ${e.message}</span>`;
    }

    btn.disabled = false;
}

/* --- FEATURE 3: OCR UPLOAD (Unchanged) --- */
async function handleFileUpload(input) {
    if (input.files && input.files[0]) {
        const formData = new FormData();
        formData.append('image', input.files[0]);

        const resultDiv = document.getElementById('ocr-result');
        resultDiv.innerHTML = "SCANNING IMAGE...";

        const response = await fetch('/api/ocr-scan/', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<span style="color:red">${data.error}</span>`;
        } else {
            const color = data.validation.is_valid ? 'var(--neon-green)' : 'var(--neon-pink)';
            resultDiv.innerHTML = `
                <h3>DETECTED TEXT: "${data.raw_text}"</h3>
                <h2 style="color: ${color}">
                    ${data.validation.is_valid ? "VALID" : "INVALID"}
                </h2>
                <p>${data.validation.final_message}</p>
            `;
        }
    }
}