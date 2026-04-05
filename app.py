import base64
import io
import numpy as np
import soundfile as sf
from flask import Flask, request, jsonify

app = Flask(__name__)

def compute_mode(arr):
    values, counts = np.unique(np.round(arr, 5), return_counts=True)
    return float(values[np.argmax(counts)])

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        audio_base64 = data.get("audio_base64", "")

        # 🔹 Fast decode
        audio_bytes = base64.b64decode(audio_base64)
        audio_buffer = io.BytesIO(audio_bytes)

        # 🔹 MUCH faster than librosa
        y, sr = sf.read(audio_buffer)

        # 🔹 If stereo → convert to mono
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)

        if len(y) == 0:
            y = np.array([0.0])

        # 🔹 Stats
        mean_val = float(np.mean(y))
        std_val = float(np.std(y))
        var_val = float(np.var(y))
        min_val = float(np.min(y))
        max_val = float(np.max(y))
        median_val = float(np.median(y))
        mode_val = compute_mode(y)
        range_val = float(max_val - min_val)

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

    except Exception:
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

@app.route('/')
def home():
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
