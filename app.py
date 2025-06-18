import base64
import io
import os

import numpy as np
from flask import Flask, send_from_directory, request, jsonify
from matplotlib import pyplot as plt
from pathlib import Path
import uuid
import shutil

# additional imports

app = Flask(__name__)

stored_traces = []
stored_heatmaps = []
HEATMAP_DIR = 'heatmaps'

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/collect_trace', methods=['POST'])
def collect_trace():
    """ 
    Implement the collect_trace endpoint to receive trace data from the frontend and generate a heatmap.
    1. Receive trace data from the frontend as JSON
    2. Generate a heatmap using matplotlib
    3. Store the heatmap and trace data in the backend temporarily
    4. Return the heatmap image and optionally other statistics to the frontend
    """
    try:
        data = request.get_json()

        # Assume trace data is a list of (x, y) coordinates
        trace = data.get('trace')
        if not trace:
            return jsonify({'error': 'Missing trace data'}), 400

        stored_traces.append(trace)

        trace_array = np.array(trace).reshape(1, -1)

        fig, ax = plt.subplots(figsize=(12, 1.5))
        cax = ax.imshow(trace_array, cmap='plasma', aspect='auto')

        ax.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        path = Path("static", HEATMAP_DIR)
        path.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.png"
        file_path = Path("static", HEATMAP_DIR, filename)
        plt.savefig(file_path)

        print(f"Heatmap saved to {file_path}")
        print(f'/static/heatmaps/{filename}')

        # Encode image to base64 string to send as JSON
        # encoded_img = base64.b64encode(buf.getvalue()).decode('utf-8')
        #
        # return jsonify({
        #     'heatmap_image': encoded_img,
        #     'samples': len(trace),
        #     'max': int(np.max(heatmap)),
        #     'min': int(np.min(heatmap)),
        # })
        return jsonify({
            'image_url': f'/static/heatmaps/{filename}',
            'samples': len(trace),
            'max': int(np.max(trace_array)),
            'min': int(np.min(trace_array)),
            'range': int(np.max(trace_array) - np.min(trace_array))
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_results', methods=['POST'])
def clear_results():
    """ 
    Implment a clear results endpoint to reset stored data.
    1. Clear stored traces and heatmaps
    2. Return success/error message
    """
    try:
        global stored_traces, stored_heatmaps
        stored_traces = []
        stored_heatmaps = []


        if os.path.exists(HEATMAP_DIR):
            shutil.rmtree(HEATMAP_DIR)

        return jsonify({'message': 'Results cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Additional endpoints can be implemented here as needed.
@app.route('/api/get_results', methods=['POST'])
def get_results():
    try:
        return jsonify({
            'traces': stored_traces,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)