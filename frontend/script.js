// CivicGuardian Voice Interface Logic
const vapi = new Vapi("2730e829-8411-4cf1-997c-9c60b57651c2");

const callBtn = document.getElementById('call-btn');
const statusText = document.getElementById('status-text');
const subStatus = document.getElementById('sub-status');
const pulseRings = document.querySelectorAll('.pulse-ring');

let isCalling = false;

vapi.on('call-start', () => {
    isCalling = true;
    statusText.innerText = "Connection Active";
    statusText.style.color = "var(--primary)";
    subStatus.innerText = "Agent securely linked via encrypted channel";
    callBtn.innerHTML = `
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="6" y="6" width="12" height="12"></rect>
        </svg>
        Terminate Session`;
    callBtn.style.background = "#b91c1c";
    
    pulseRings.forEach(ring => ring.style.animationDuration = "1s");
});

// Accessibility Toggles
const contrastBtn = document.getElementById('contrast-toggle');
contrastBtn.addEventListener('click', () => {
    document.body.classList.toggle('high-contrast');
    const isActive = document.body.classList.contains('high-contrast');
    contrastBtn.innerText = isActive ? "Enabled" : "Disabled";
    contrastBtn.classList.toggle('active', isActive);
});

const sizeBtn = document.getElementById('text-size-toggle');
sizeBtn.addEventListener('click', () => {
    document.body.classList.toggle('large-text');
    const isLarge = document.body.classList.contains('large-text');
    sizeBtn.innerText = isLarge ? "Large" : "Standard";
    sizeBtn.classList.toggle('active', isLarge);
});

vapi.on('speech-update', (update) => {
    if (update.type === 'transcript' && update.transcriptType === 'partial') {
        const transcriptDiv = document.getElementById('transcript');
        transcriptDiv.innerHTML = `<p>${update.text}</p>`;
        transcriptDiv.scrollTop = transcriptDiv.scrollHeight;
    }
});

vapi.on('speech-end', () => {
    // Keep the final transcript visible for a moment
});

vapi.on('call-end', () => {
    isCalling = false;
    statusText.innerText = "System Ready";
    statusText.style.color = "var(--text)";
    subStatus.innerText = "Awaiting voice command initialization";
    callBtn.innerHTML = `
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
        </svg>
        Initiate Voice Protocol`;
    callBtn.style.background = "var(--primary)";
    
    pulseRings.forEach(ring => ring.style.animationDuration = "3s");
});

vapi.on('error', (error) => {
    console.error('Vapi Error:', error);
    statusText.innerText = "Protocol Offline";
    subStatus.innerText = "Check cryptographic keys and infrastructure status.";
});

callBtn.addEventListener('click', () => {
    if (isCalling) {
        vapi.stop();
    } else {
        // You can find your Assistant ID in the Vapi Dashboard
        const assistantId = "024574ad-baac-4ffd-b038-eddadb4e2735"; 
        
        if (assistantId === "YOUR_ASSISTANT_ID_HERE") {
            alert("Please set your Assistant ID in script.js to start the call.");
            return;
        }
        
        statusText.innerText = "Connecting...";
        vapi.start(assistantId);
    }
});
