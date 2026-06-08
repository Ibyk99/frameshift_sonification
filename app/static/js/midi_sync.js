function initializeSync() {
    const player = document.getElementById('midiPlayer');

    if (!player) {
        console.error('MIDI player not found');
        return;
    }

    const tempo = 140;
    const quarterNoteMs = (60 / tempo) * 1000;

    const geneticCode = {
        'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
        'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
        'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
        'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
        'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
        'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
        'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
        'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
        'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
        'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
        'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
        'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
        'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
        'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
        'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
        'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
    };

    function translateCodon(codon) {
        const upper = codon.toUpperCase().replace(/U/g, 'T');
        return geneticCode[upper] || '?';
    }

    function wrapBases(element) {
        const text = element.textContent;
        element.innerHTML = '';
        let codonCount = 0;
        let codonSpan = null;

        for (let i = 0; i < text.length; i++) {
            const char = text[i];

            if (codonCount % 3 === 0) {
                codonSpan = document.createElement('span');
                codonSpan.className = 'codon';
                element.appendChild(codonSpan);
            }

            if (char !== '-') {
                const span = document.createElement('span');
                span.className = 'base';
                span.textContent = char;
                codonSpan.appendChild(span);
                codonCount++;
            } else {
                const span = document.createElement('span');
                span.className = 'gap';
                span.textContent = '-';
                codonSpan.appendChild(span);
            }
        }
    }

    function highlightBase(baseIndex) {
        document.querySelectorAll('.base.active').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.codon.active').forEach(el => el.classList.remove('active', 'match', 'mismatch'));

        const queryBases = document.getElementById('queryBases').querySelectorAll('.base');
        const subjectBases = document.getElementById('subjectBases').querySelectorAll('.base');
        const queryCodens = document.getElementById('queryBases').querySelectorAll('.codon');
        const subjectCodens = document.getElementById('subjectBases').querySelectorAll('.codon');

        if (queryBases[baseIndex]) {
            queryBases[baseIndex].classList.add('active');
            const codonIndex = Math.floor(baseIndex / 3);
            if (queryCodens[codonIndex]) {
                queryCodens[codonIndex].classList.add('active');

                const queryCodon = queryCodens[codonIndex].textContent;
                const subjectCodon = subjectCodens[codonIndex].textContent;

                const queryAA = translateCodon(queryCodon);
                const subjectAA = translateCodon(subjectCodon);

                if (queryAA === subjectAA) {
                    queryCodens[codonIndex].classList.add('match');
                    if (subjectCodens[codonIndex]) {
                        subjectCodens[codonIndex].classList.add('active', 'match');
                    }
                } else {
                    queryCodens[codonIndex].classList.add('mismatch');
                    if (subjectCodens[codonIndex]) {
                        subjectCodens[codonIndex].classList.add('active', 'mismatch');
                    }
                }
            }
        }

        if (subjectBases[baseIndex]) {
            subjectBases[baseIndex].classList.add('active');
        }
    }

    wrapBases(document.getElementById('queryBases'));
    wrapBases(document.getElementById('subjectBases'));

    setInterval(() => {
        if (player.currentTime !== undefined) {
            const currentTimeMs = player.currentTime * 1000;
            const baseIndex = Math.floor(currentTimeMs / quarterNoteMs) + 1;
            highlightBase(baseIndex);
        }
    }, 16);

    player.addEventListener('stop', () => {
        document.querySelectorAll('.base.active').forEach(el => el.classList.remove('active'));
    });

    console.log('MIDI sync initialized');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSync);
} else {
    setTimeout(initializeSync, 100);
}
