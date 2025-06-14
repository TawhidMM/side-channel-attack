import base64
import io
import numpy as np
from flask import Flask, send_from_directory, request, jsonify
from matplotlib import pyplot as plt
import os
import uuid

# additional imports

app = Flask(__name__)

stored_traces = []
stored_heatmaps = []

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

        # stored_traces.append(trace)

        # Convert trace into a 2D histogram
        # trace_np = np.array(trace)
        trace_array = np.array(trace).reshape(1, -1)  # Shape: (1, N)

        fig, ax = plt.subplots(figsize=(12, 1.5))  # Wide and short
        cax = ax.imshow(trace_array, cmap='plasma', aspect='auto')

        ax.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # Save to buffer
        # buf = io.BytesIO()
        # plt.savefig(buf, format='png')
        # buf.seek(0)
        # plt.close(fig)

        save_dir = 'static/heatmaps'
        os.makedirs(save_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.png"
        file_path = os.path.join(save_dir, filename)
        plt.savefig(file_path)

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


# Additional endpoints can be implemented here as needed.

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)