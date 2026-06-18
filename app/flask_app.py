from flask import Flask, render_template, request, session, redirect, send_file
from flask_session import Session
from Bio.Blast import NCBIXML
from datetime import datetime as dt
import settings
from midiutil import MIDIFile
import sound_mappings as sound_mappings
from sonification_functions import build_track_codon, build_track_nuc, build_track
import os
import logging

app = Flask(__name__)
app.secret_key = settings.secret_key

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def load_alignments(file_obj):
    alignments = []
    for blast_record in NCBIXML.parse(file_obj):
        for alignment in blast_record.alignments:
            if alignment.hsps:
                hsp = alignment.hsps[0]
                alignments.append({
                    'query': hsp.query,
                    'subject': hsp.sbjct,
                    'match': hsp.match,
                    'evalue': hsp.expect,
                    'bits': hsp.bits,
                    'query_frame': hsp.frame[0],
                    'subject_frame': hsp.frame[1],
                    'hit_def': alignment.title,
                    'accession': alignment.accession
                })
    return alignments


# Route for uploading an XML file and viewing the alignments within it
@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        if 'xml_file' in request.files:
            file = request.files['xml_file']
            session["filename"] = file.filename
            try:
                result = load_alignments(file)
                session['alignments'] = result
                return redirect('/alignments')
            except PermissionError as e:
                error = f"Can't read file - please check the permissions on the file > {e}"
                return render_template('index.html', error=error), 400
            except Exception as e:
                error = f"Failed to read XML file - please ensure a valid XML file has been provided > {e}"
                return render_template('index.html', error=error), 400
        elif request.form.get('load_example') == 'true':
            try:
                with open(settings.example_file, 'r') as f:
                    result = load_alignments(f)
                    session['alignments'] = result
                    session['filename'] = 'Example: combined_blast_alignment.xml'
                    return redirect('/alignments')
            except Exception as e:
                error = f"Failed to load example dataset > {e}"
                return render_template('index.html', error=error), 400

    return render_template('index.html', error=error), 200


# Route for displaying the alignments list
@app.route('/alignments')
def alignments():
    alignments = session.get('alignments', [])
    filename = session.get('filename')
    if not alignments:
        return redirect('/')
    return render_template('alignments.html', alignments=alignments, filename=filename), 200


# Route for viewing an individual selected alignment from the above page
@app.route('/alignments/<int:index>')
def alignment_results(index):
    try:
        midi_file = request.args.get('midi_file') # Add some file validation stuff
    except:
        midi_file = None
    alignments = session.get('alignments', [])
    print(f"DEBUG: index={index}, alignments count={len(alignments)}")  # Add this
    if len(alignments) != 0:
        if index >= 0 and index < len(alignments):
            alignment = alignments[index]

            return render_template('results.html', alignment=alignment, midi_file=midi_file, index=index)
    return render_template('not_found.html', message="Alignment not found"), 404


# Route to serve MIDI files from temp directory
@app.route('/temp/<filename>')
def serve_midi(filename):
    full_path = f"{settings.out_file_path}/{filename}"
    return send_file(full_path, mimetype='audio/midi')


def delete_midi_file_helper(midi_filename):
    if '/' in midi_filename or '\\' in midi_filename or '~' in midi_filename:
        return
    full_path = f"{settings.out_file_path}/{midi_filename}"
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        print(f"Error deleting MIDI file: {e}")


@app.route('/alignments/cleanup/<midi_filename>')
def delete_midi_file(midi_filename):
    delete_midi_file_helper(midi_filename)
    redirect_to = request.args.get('redirect_to', '/alignments')
    return redirect(redirect_to)


# Endpoint to generate a midi file for a given alignment
@app.route('/alignments/sonify', methods =['POST'])
def generate_sonification():
    if request.method == 'POST':

        # Delete old MIDI file if it exists
        old_midi_file = request.form.get('old_midi_file')
        if old_midi_file:
            delete_midi_file_helper(old_midi_file)

        # Init a midi file with 2 tracks
        # We don't want to adjust the origin as we may have some leading silences
        midi_file = MIDIFile(2, adjust_origin=False)
        time = 0
        tempo = 140
        query_seq = request.form.get('query_seq')
        subject_seq = request.form.get('subject_seq')
        index = request.form.get('index')
        stop_codon = request.form.get('stop_codon')
        codon_or_nuc = request.form.get('codon_or_nuc')


        # Build both tracks - 1 for query seq and 1 for subject seq
        track = 0
        stop_at_codon = True if stop_codon == "yes" else False
        sonify_codons = False if codon_or_nuc == 'nucleotides' else True
        sonify_nucs = False if codon_or_nuc == 'codons' else True

        seq_config = {
            query_seq: {"nuc_inst": 11 ,
                        "codon_inst": 1},
            subject_seq: {"nuc_inst": 73 ,
                          "codon_inst": 42}
                                    }
        
        for seq in [query_seq, subject_seq]:
            midi_file.addTrackName(track, time, f"track_{track}")
            midi_file.addTempo(track, time, tempo)

            build_track(
                sequence=seq,
                track=track,
                midi=midi_file,
                stop=stop_at_codon,
                codons=sonify_codons,
                nucs=sonify_nucs,
                b_map=sound_mappings.base_map,
                c_map=sound_mappings.codons,
                codon_inst=seq_config[seq]["codon_inst"],
                nuc_inst=seq_config[seq]["nuc_inst"]
            )

            track += 1

        # Write to midi file
        now = dt.now()
        output_file = f"output_file_{now.strftime('%Y-%m-%d_%H-%M-%S_%f')}"
        out_path_and_file = f"{settings.out_file_path}/{output_file}.mid"

        with open(out_path_and_file, "wb") as outfile:
            midi_file.writeFile(outfile)

        return redirect(f'/alignments/{int(index)}?midi_file={output_file}.mid')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
