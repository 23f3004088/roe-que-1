import base64
import io
import numpy as np
import librosa
from flask import Flask, request, jsonify

app = Flask(__name__)

def compute_mode(arr):
    # approximate mode for continuous values
    values, counts = np.unique(np.round(arr, 5), return_counts=True)
    return float(values[np.argmax(counts)])

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        audio_base64 = data.get("audio_base64", "")

        # 🔹 Step 1: Decode base64 → audio bytes
        audio_bytes = base64.b64decode(audio_base64)

        # 🔹 Step 2: Load audio using librosa
        audio_buffer = io.BytesIO(audio_bytes)
        y, sr = librosa.load(audio_buffer, sr=None)

        # 🔹 Step 3: If empty audio
        if len(y) == 0:
            y = np.array([0.0])

        # 🔹 Step 4: Compute statistics
        mean_val = float(np.mean(y))
        std_val = float(np.std(y))
        var_val = float(np.var(y))
        min_val = float(np.min(y))
        max_val = float(np.max(y))
        median_val = float(np.median(y))
        mode_val = compute_mode(y)
        range_val = float(max_val - min_val)

        # 🔹 Step 5: Build STRICT JSON
        result = {
            "rows": int(len(y)),
            "columns": ["amplitude"],
            "mean": {"amplitude": mean_val},
            "std": {"amplitude": std_val},
            "variance": {"amplitude": var_val},
            "min": {"amplitude": min_val},
            "max": {"amplitude": max_val},
            "median": {"amplitude": median_val},
            "mode": {"amplitude": mode_val},
            "range": {"amplitude": range_val},
            "allowed_values": {},
            "value_range": {"amplitude": [min_val, max_val]},
            "correlation": []
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "rows": 0,
            "columns": [],
            "mean": {},
            "std": {},
            "variance": {},
            "min": {},
            "max": {},
            "median": {},
            "mode": {},
            "range": {},
            "allowed_values": {},
            "value_range": {},
            "correlation": []
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
