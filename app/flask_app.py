from flask import Flask, render_template, request, session, abort
from Bio.Blast import NCBIXML
from datetime import datetime as dt
import settings
from midiutil import MIDIFile
import sound_mappings as sound_mappings
from sonficiation_tool import build_track_codon, build_track_nuc

app = Flask(__name__)
app.secret_key = 'frameshift_sonification_secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        if 'xml_file' in request.files:
            file = request.files['xml_file']
            try:
                blast_record = NCBIXML.read(file)
                alignments = []
                for alignment in blast_record.alignments:
                    if alignment.hsps:
                        hsp = alignment.hsps[0]
                        alignments.append({
                            'query': hsp.query,
                            'subject': hsp.sbjct,
                            'match': hsp.match,
                            'evalue': hsp.expect,
                            'bits': hsp.bits
                        })
                result = alignments
                session['alignments'] = alignments
            except PermissionError as e:
                error = f"Can't read file - please check the permissions on the file > {e}"
                return render_template('index.html', error=error), 400
            except Exception as e:
                error = f"Failed to read XML file - please ensure a valid XML file has been provided > {e}"
                return render_template('index.html', error=error), 400
    else:
        # Display alignments from session if no new file was uploaded - stops page from clearing if we revisit
        result = session.get('alignments')

    status_code = 400 if error else 200 # HTTP status code
    return render_template('index.html', result=result, error=error), status_code



@app.route('/alignment/<int:index>')
def alignment_results(index):
    alignments = session.get('alignments', [])
    if len(alignments) != 0:
        if index >= 0 and index < len(alignments):
            alignment = alignments[index]

            return render_template('results.html', alignment=alignment)
    return render_template('not_found.html', message=alignment), 404 # TODO: Render a 404 page



@app.route('/alignment/sonify', methods =['POST'])
def generate_sonification():
    if request.method == 'POST':
        # Init a midi file with 2 tracks
        # We don't want to adjust the origin as we may have some leading silences
        midi_file = MIDIFile(2, adjust_origin=False)
        time = 0
        tempo = 140

        query_seq = request.form.get('query_seq')
        subject_seq = request.form.get('subject_seq')

        # Build both tracks - 1 for query seq and 1 for subject seq
        track = 0
        for seq in [query_seq, subject_seq]:
            midi_file.addTrackName(track, time, f"track_{track}")
            midi_file.addTempo(track, time, tempo)
            build_track_nuc(seq, track, midi_file, sound_mappings.base_map)
            build_track_codon(seq, track, midi_file, sound_mappings.codons)
            print(f"track_{track}", seq)
            track += 1

        # Write to midi file
        now = dt.now()
        output_file = f"output_file_{now.strftime('%Y-%m-%d_%H-%M-%S_%f')}"
        out_path_and_file = f"{settings.out_file_path}/{output_file}.mid"

        with open(out_path_and_file, "wb") as outfile:
            midi_file.writeFile(outfile)

        return "success", 200




if __name__ == '__main__':
    app.run(debug=True)
