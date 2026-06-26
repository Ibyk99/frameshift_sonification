function initializeSync() {
    const player = document.getElementById('midiPlayer');
    if (!player) {
        console.error('MIDI player not found');
        return;
    }

    const TEMPO = 140;
    const BEATS_PER_SECOND = TEMPO / 60;
    const EPSILON = 0.0001;

    const GENETIC_CODE = {
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
        return GENETIC_CODE[upper] || '?';
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

            const span = document.createElement('span');
            span.textContent = char;
            codonSpan.appendChild(span);

            if (char !== '-') {
                span.className = 'base';
                codonCount++;
            } else {
                span.className = 'gap';
            }
        }
    }

    const queryContainer = document.getElementById('queryBases');
    const subjectContainer = document.getElementById('subjectBases');

    wrapBases(queryContainer);
    wrapBases(subjectContainer);

    const queryBases = queryContainer.querySelectorAll('.base');
    const subjectBases = subjectContainer.querySelectorAll('.base');
    const queryCodons = queryContainer.querySelectorAll('.codon');
    const subjectCodons = subjectContainer.querySelectorAll('.codon');

    function buildTimeMapping(container) {
        // Build a map of all characters (bases and gaps) with their indices
        const allElements = [];
        let baseIndex = 0;

        const codons = Array.from(container.querySelectorAll('.codon'));
        for (let codonIndex = 0; codonIndex < codons.length; codonIndex++) {
            const codon = codons[codonIndex];
            for (const child of codon.children) {
                if (child.classList.contains('base')) {
                    allElements.push({
                        type: 'base',
                        index: baseIndex++,
                        codonIndex: codonIndex,
                        element: child
                    });
                } else {
                    allElements.push({
                        type: 'gap',
                        codonIndex: codonIndex,
                        element: child
                    });
                }
            }
        }

        // Build mapping from MIDI beat (base index) to character position
        const mapping = [];
        for (let baseIdx = 0; baseIdx < baseIndex; baseIdx++) {
            let charPos = 0;
            let currentBaseIdx = 0;

            // Find the character position of this base
            for (let i = 0; i < allElements.length; i++) {
                if (allElements[i].type === 'base') {
                    if (currentBaseIdx === baseIdx) {
                        charPos = i;
                        break;
                    }
                    currentBaseIdx++;
                }
            }

            mapping.push(allElements[charPos]);
        }

        return mapping;
    }

    const queryTimeMap = buildTimeMapping(queryContainer);
    const subjectTimeMap = buildTimeMapping(subjectContainer);

    const state = {
        queryStopCodonIndex: null,
        subjectStopCodonIndex: null,
        lastBaseIndex: -1
    };

    function getCodonAA(codonIndex, codons) {
        if (!codons[codonIndex]) return null;
        const bases = Array.from(codons[codonIndex].querySelectorAll('.base'))
            .map(el => el.textContent).join('');
        return translateCodon(bases);
    }

    function clearHighlighting() {
        queryBases.forEach(el => el.classList.remove('active'));
        subjectBases.forEach(el => el.classList.remove('active'));
        queryCodons.forEach(el => el.classList.remove('active', 'match', 'mismatch'));
        subjectCodons.forEach(el => el.classList.remove('active', 'match', 'mismatch'));
        document.querySelectorAll('.gap.active').forEach(el => el.classList.remove('active'));
    }

    function updateHighlighting(baseIndex, codonIndex) {
        const mode = localStorage.getItem('codon_or_nuc') || 'both';
        const showNucleotides = mode === 'nucleotides' || mode === 'both';
        const showCodons = mode === 'codons' || mode === 'both';

        const queryAA = getCodonAA(codonIndex, queryCodons);
        const subjectAA = getCodonAA(codonIndex, subjectCodons);

        if (showNucleotides) {
            if (queryBases[baseIndex]) queryBases[baseIndex].classList.add('active');
            if (subjectBases[baseIndex]) subjectBases[baseIndex].classList.add('active');
        }

        if (showCodons && queryCodons[codonIndex]) {
            if (queryAA === '*') {
                queryCodons[codonIndex].classList.add('stop-codon');
            } else if (!state.queryStopCodonIndex) {
                queryCodons[codonIndex].classList.add('active');
                queryCodons[codonIndex].classList.add(queryAA === subjectAA ? 'match' : 'mismatch');
            }
        }

        if (showCodons && subjectCodons[codonIndex]) {
            if (subjectAA === '*') {
                subjectCodons[codonIndex].classList.add('stop-codon');
            } else if (!state.subjectStopCodonIndex) {
                subjectCodons[codonIndex].classList.add('active');
                subjectCodons[codonIndex].classList.add(queryAA === subjectAA ? 'match' : 'mismatch');
            }
        }

        if (showCodons) {
            if (state.queryStopCodonIndex !== null && queryCodons[state.queryStopCodonIndex]) {
                queryCodons[state.queryStopCodonIndex].classList.add('stop-codon');
            }
            if (state.subjectStopCodonIndex !== null && subjectCodons[state.subjectStopCodonIndex]) {
                subjectCodons[state.subjectStopCodonIndex].classList.add('stop-codon');
            }
        }
    }

    function checkStopCodons(baseIndex, codonIndex) {
        if (localStorage.getItem('stop_codon') !== 'yes') return;

        if (state.queryStopCodonIndex === null && getCodonAA(codonIndex, queryCodons) === '*') {
            state.queryStopCodonIndex = codonIndex;
        }

        if (state.subjectStopCodonIndex === null && getCodonAA(codonIndex, subjectCodons) === '*') {
            state.subjectStopCodonIndex = codonIndex;
        }
    }

    function update() {
        if (player.currentTime === undefined) {
            requestAnimationFrame(update);
            return;
        }

        const midiTime = Math.floor(player.currentTime * BEATS_PER_SECOND + EPSILON);
        const queryElement = queryTimeMap[midiTime];
        const subjectElement = subjectTimeMap[midiTime];

        clearHighlighting();

        if (queryElement) {
            if (queryElement.type === 'base') {
                const baseIndex = queryElement.index;
                const codonIndex = queryElement.codonIndex;

                if (baseIndex > state.lastBaseIndex + 3) {
                    if (state.queryStopCodonIndex !== null && codonIndex > state.queryStopCodonIndex) {
                        state.queryStopCodonIndex = null;
                    }
                    if (state.subjectStopCodonIndex !== null && codonIndex > state.subjectStopCodonIndex) {
                        state.subjectStopCodonIndex = null;
                    }
                }

                checkStopCodons(baseIndex, codonIndex);
                updateHighlighting(baseIndex, codonIndex);

                // Also highlight gaps within the current codon
                if (queryCodons[codonIndex]) {
                    queryCodons[codonIndex].querySelectorAll('.gap').forEach(gap => {
                        gap.classList.add('active');
                    });
                }
                if (subjectCodons[codonIndex]) {
                    subjectCodons[codonIndex].querySelectorAll('.gap').forEach(gap => {
                        gap.classList.add('active');
                    });
                }

                state.lastBaseIndex = baseIndex;
            }
        }

        if (subjectElement) {
            const subjectCodonIndex = subjectElement.codonIndex;
            if (subjectCodons[subjectCodonIndex]) {
                subjectCodons[subjectCodonIndex].querySelectorAll('.gap').forEach(gap => {
                    gap.classList.add('active');
                });
            }
        }

        requestAnimationFrame(update);
    }

    player.addEventListener('stop', () => {
        clearHighlighting();
        queryCodons.forEach(el => el.classList.remove('stop-codon'));
        subjectCodons.forEach(el => el.classList.remove('stop-codon'));
        state.queryStopCodonIndex = null;
        state.subjectStopCodonIndex = null;
        state.lastBaseIndex = -1;
    });

    requestAnimationFrame(update);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSync);
} else {
    setTimeout(initializeSync, 100);
}
