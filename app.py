import os
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from llm import generate_llm_advisory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Load the trained model
model = tf.keras.models.load_model('trained_model.keras')

# Class names
CLASS_NAMES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image_path):
    """
    Preprocess the image EXACTLY like in your notebook:

    image = tf.keras.preprocessing.image.load_img(image_path, target_size=(128,128))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    """
    # Load image (resizes to 128x128)
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(128, 128))

    # Convert to array
    input_arr = tf.keras.preprocessing.image.img_to_array(img)

    # Convert single image to batch
    input_arr = np.array([input_arr])  # shape: (1, 128, 128, 3)

    # IMPORTANT: No /255.0 here because notebook also uses raw 0–255 values
    return input_arr


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Preprocess the image
            processed_image = preprocess_image(filepath)

            # Make prediction
            predictions = model.predict(processed_image)
            predicted_class_idx = int(np.argmax(predictions[0]))
            confidence = float(predictions[0][predicted_class_idx])

            # Get top 3 predictions
            top_3_indices = np.argsort(predictions[0])[-3:][::-1]
            top_3_predictions = []

            for idx in top_3_indices:
                class_name = CLASS_NAMES[int(idx)]
                class_confidence = float(predictions[0][idx])
                is_healthy = 'healthy' in class_name.lower()

                top_3_predictions.append({
                    'class': class_name,
                    'confidence': round(class_confidence * 100, 2),
                    'is_healthy': is_healthy
                })

            predicted_class = CLASS_NAMES[predicted_class_idx]
            is_healthy = 'healthy' in predicted_class.lower()
            # Generate LLM advisory
            llm_advisory = generate_llm_advisory(predicted_class, confidence)
            print(llm_advisory)

            return jsonify({
                'success': True,
                'prediction': predicted_class,
                'confidence': round(confidence * 100, 2),
                'is_healthy': is_healthy,
                'image_url': filepath,
                'all_predictions': top_3_predictions,
                'llm_advisory': llm_advisory

            })

        except Exception as e:
            return jsonify({'error': f'Error during prediction: {str(e)}'}), 500

    return jsonify({'error': 'Invalid file type. Please upload a PNG, JPG, or JPEG image.'}), 400


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
