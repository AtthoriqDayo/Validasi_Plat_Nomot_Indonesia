/* --- NAVIGATION SYSTEM --- */
function showSection(id) {
    document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById('section-' + id).classList.add('active');
    
    const map = {'visualizer': 0, 'performance': 1, 'ocr': 2};
    document.querySelectorAll('.nav-item')[map[id]].classList.add('active');
}


/* --- PETA KONEKSI DFA (Definisi Struktur) --- */
const dfaTransitions = [
    // Jalur Utama (Valid)
    { from: 'node-q0', to: 'node-q_check_region' },
    { from: 'node-q_check_region', to: 'node-q_space1' }, // spasi setelah 1 huruf
    { from: 'node-q_check_region', to: 'node-q_region_done' }, // huruf ke-2
    { from: 'node-q_region_done', to: 'node-q_space1' },
    { from: 'node-q_space1', to: 'node-q_digit1' },
    { from: 'node-q_digit1', to: 'node-q_digit2' },
    { from: 'node-q_digit1', to: 'node-q_space2' }, // 1 angka lalu spasi
    { from: 'node-q_digit2', to: 'node-q_digit3' },
    { from: 'node-q_digit2', to: 'node-q_space2' }, // 2 angka lalu spasi
    { from: 'node-q_digit3', to: 'node-q_digit4' },
    { from: 'node-q_digit3', to: 'node-q_space2' }, // 3 angka lalu spasi
    { from: 'node-q_digit4', to: 'node-q_space2' },
    { from: 'node-q_space2', to: 'node-q_final1' },
    { from: 'node-q_final1', to: 'node-q_final2' },
    { from: 'node-q_final2', to: 'node-q_final3' }
];

/* --- INIT VISUALIZER --- */
document.addEventListener('DOMContentLoaded', () => {
    // Gambar garis statis saat halaman dimuat
    setTimeout(drawDFAGraph, 500); 
    // Gambar ulang jika window di-resize (responsif)
    window.addEventListener('resize', drawDFAGraph);
});

/* --- FUNGSI MENGGAMBAR GARIS (SVG ENGINE) --- */
function drawDFAGraph() {
    const svg = document.getElementById('dfa-lines-layer');
    const container = document.getElementById('dfaContainer');
    if(!svg || !container) return;

    svg.innerHTML = ''; // Reset garis

    // Definisikan Arrowhead Marker di SVG
    svg.innerHTML = `
        <defs>
            <marker id="arrow-cyan" markerWidth="10" markerHeight="10" refX="20" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="#00f3ff" />
            </marker>
            <marker id="arrow-pink" markerWidth="10" markerHeight="10" refX="20" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="#ff0055" />
            </marker>
        </defs>
    `;

    // 1. Gambar Garis Valid (DFA Transitions)
    dfaTransitions.forEach(conn => {
        createLine(conn.from, conn.to, 'valid');
    });

    // 2. Gambar Garis ke TRAP (Semua node valid punya potensi ke TRAP)
    const allNodes = document.querySelectorAll('.node:not(#node-TRAP)');
    allNodes.forEach(node => {
        createLine(node.id, 'node-TRAP', 'trap');
    });
}
/* --- FUNGSI MENGGAMBAR GARIS (Updated: Edge-to-Edge) --- */
function createLine(id1, id2, type) {
    const el1 = document.getElementById(id1);
    const el2 = document.getElementById(id2);
    const svg = document.getElementById('dfa-lines-layer');
    
    if (!el1 || !el2) return;

    // 1. Ambil Koordinat Pusat Node
    const rect1 = el1.getBoundingClientRect();
    const rect2 = el2.getBoundingClientRect();
    const contRect = document.getElementById('dfaContainer').getBoundingClientRect();

    // Pusat Node 1
    const x1 = rect1.left + rect1.width / 2 - contRect.left;
    const y1 = rect1.top + rect1.height / 2 - contRect.top;
    
    // Pusat Node 2
    const x2 = rect2.left + rect2.width / 2 - contRect.left;
    const y2 = rect2.top + rect2.height / 2 - contRect.top;

    // 2. HITUNG OFFSET (Agar garis mulai dari pinggir, bukan tengah)
    // Radius node = 30px (karena width 60px). Kita tambah 5px jarak aman.
    const r = 42.5; 
    
    // Hitung jarak dan sudut (Vektor)
    const dx = x2 - x1;
    const dy = y2 - y1;
    const dist = Math.sqrt(dx*dx + dy*dy);
    
    // Jika jarak 0 (error), hentikan
    if (dist === 0) return;

    // Unit Vektor (Arah)
    const ux = dx / dist;
    const uy = dy / dist;

    // Koordinat Baru (Di pinggir lingkaran)
    // Start: Geser dari pusat 1 ke arah 2 sejauh radius
    const startX = x1 + (ux * r);
    const startY = y1 + (uy * r);
    
    // End: Geser dari pusat 2 mundur ke arah 1 sejauh radius
    const endX = x2 - (ux * r);
    const endY = y2 - (uy * r);

    // 3. Buat Garis SVG
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    
    let d = '';
    if (type === 'trap') {
        // Logika Kurva untuk TRAP:
        // Kita gunakan start/end yang sudah dipotong agar rapi
        // Control point ditarik sedikit ke bawah agar melengkung
        const ctrlX = startX; 
        const ctrlY = endY - 50; 
        d = `M${startX},${startY} Q${ctrlX},${ctrlY} ${endX},${endY}`;
    } else {
        // Garis Lurus untuk flow utama
        d = `M${startX},${startY} L${endX},${endY}`;
    }

    path.setAttribute('d', d);
    path.setAttribute('id', `line-${id1}-${id2}`);
    path.classList.add('connection-line');
    
    if (type === 'trap') {
        path.classList.add('to-trap');
        path.setAttribute('marker-end', 'url(#arrow-pink)');
    } else {
        path.setAttribute('marker-end', 'url(#arrow-cyan)');
    }

    svg.appendChild(path);
}

/* --- LOGIKA RUN VISUALIZER (UPDATED) --- */
async function runVisualizer() {
    const input = document.getElementById('plateInput').value;
    const statusText = document.getElementById('statusText');
    
    if (!input) return;

    // Reset UI (Hapus semua kelas aktif)
    document.querySelectorAll('.node').forEach(n => n.classList.remove('active-neon', 'trap-state'));
    document.querySelectorAll('.connection-line').forEach(l => l.classList.remove('active-path', 'active-trap'));

    statusText.innerText = "INITIALIZING PROTOCOLS...";
    statusText.style.color = "var(--text-main)";

    try {
        const response = await fetch(`/api/validate-dfa/?plate=${encodeURIComponent(input)}`);
        const data = await response.json();

        let prevState = null;

        // Loop Animasi
        for (let step of data.history) {
            const currState = 'node-' + step.state;
            const currNode = document.getElementById(currState);
            
            // 1. Highlight Garis (Transisi dari Prev -> Curr)
            if (prevState) {
                // Coba cari garis valid
                let lineId = `line-${prevState}-${currState}`;
                let lineEl = document.getElementById(lineId);
                
                // Jika tidak ada garis langsung (berarti ini masuk ke TRAP secara logika aplikasi)
                if (!lineEl && step.state === 'TRAP') {
                    lineId = `line-${prevState}-node-TRAP`;
                    lineEl = document.getElementById(lineId);
                }

                if (lineEl) {
                    const isTrap = step.state === 'TRAP';
                    lineEl.classList.add(isTrap ? 'active-trap' : 'active-path');
                }
            }

            // 2. Highlight Node
            if (currNode) {
                if (step.state === 'TRAP') {
                    currNode.classList.add('trap-state');
                    statusText.innerText = `ERROR: ${step.reason}`; 
                    statusText.style.color = "var(--neon-pink)";
                } else {
                    currNode.classList.add('active-neon');
                    const char = step.input ? `Input: '${step.input}'` : 'Start';
                    statusText.innerText = `${char} >> State: ${step.state}`;
                }
            }

            // Jeda waktu agar mata bisa mengikuti garis
            await new Promise(r => setTimeout(r, 800));
            
            // Persiapan step berikutnya (Matikan highlight garis sebelumnya agar rapi)
             if (prevState) {
                 // Opsional: Jika ingin garis tetap menyala sebagai "jejak", hapus bagian remove ini
                 // document.getElementById(...)?.classList.remove('active-path');
             }
             prevState = currState;
        }

        // Final Result Text
        if (data.is_valid) {
            statusText.innerText = "ACCESS GRANTED: VALID PLATE";
            statusText.style.color = "var(--neon-green)";
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