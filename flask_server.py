import pandas as pd
from flask import Flask, request, jsonify, render_template, send_file, abort
from joblib import load
import constant
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads/'
loaded_model = load("./models/model.joblib")


@app.route('/custom-input', methods=['POST'])
def process_payload():
    try:
        data = request.get_json()

        residue_count = data.get('residueCountSeq', '')
        resolution = data.get('resolution', '')
        molecular_weight = data.get('structureMolecularWeight', '')
        density_matthews = data.get('densityMatthews', '')
        density_percent_sol = data.get('densityPercentSol', '')
        ph_value = data.get('phValue', '')

        response_data = {
            'residueCount': len(residue_count.strip()),
            'resolution': resolution,
            'structureMolecularWeight': molecular_weight,
            'densityMatthews': density_matthews,
            'densityPercentSol': density_percent_sol,
            'phValue': ph_value,
        }
        df = pd.DataFrame([response_data])
        print(df)
        res = loaded_model.predict(df)
        df['Protein Code'] = res
        df['Protein Name'] = df['Protein Code'].map(constant.protein)
        df.fillna('NA', inplace=True)
        json_data = df.to_dict(orient='records')

        return jsonify(json_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('upload.html')

    if 'files' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['files']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    allowed_extensions = ['xlsx', 'xls', 'csv']
    if not file.filename.split('.')[-1].lower() in allowed_extensions:
        return jsonify({'error': 'Invalid file extension. Only Excel or CSV files are allowed'}), 400

    # try:
    if 1:
        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file, engine='openpyxl')
        else:
            df = pd.read_csv(file)


        df['fastaSequence'] = df['fastaSequence'].apply(lambda x: len(str(x).strip()))
        df.rename(columns={'fastaSequence': 'residueCount'}, inplace=True)
        
        print(df)
        res = loaded_model.predict(df)
        
        df['Protein Code'] = res
        df['Protein Name'] = df['Protein Code'].map(constant.protein)
        df.fillna('NA', inplace=True)
        json_data = df.to_dict(orient='records')

        return jsonify(json_data), 200

    # except Exception as e:
    #     return jsonify({'error': f'Error reading file: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
