from flask import Flask, render_template, request
from Bio.Blast import NCBIXML

app = Flask(__name__)

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
            except Exception as e:
                error = f"Failed to read XML file - please make sure it's valid > {e}"

    return render_template('index.html', result=result, error=error)



if __name__ == '__main__':
    app.run(debug=True)
