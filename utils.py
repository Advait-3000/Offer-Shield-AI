import os
import json
import google.generativeai as genai
import numpy as np

# We import keras for model loading, but wrap it in try-except in case it's not installed yet
try:
    import tensorflow as tf
except ImportError:
    tf = None

from dotenv import load_dotenv
from prompts import EXTRACTION_PROMPT, EXPLANATION_PROMPT

load_dotenv()

def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    genai.configure(api_key=api_key)
    # Using a modern gemini model for extraction and explanation
    return genai.GenerativeModel("gemini-1.5-flash")

def clean_json_response(response_text: str) -> dict:
    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())

def extract_features(text: str) -> dict:
    model = get_gemini_model()
    prompt = EXTRACTION_PROMPT.format(text=text[:5000])
    response = model.generate_content(prompt)
    try:
        return clean_json_response(response.text)
    except Exception as e:
        # Fallback if json parsing fails
        return {
            "job_id": None,
            "title": None,
            "description": None,
            "department": None,
            "has_company_logo": None,
            "employment_type": None
        }

def prepare_ml_input(extracted_json: dict):
    # Depending on the exact Keras model architecture, you might need to
    # convert this dictionary into a specific tensor or array format.
    # We will pass the dictionary's values as strings or categorical inputs.
    
    # As a placeholder format, returning a 2D numpy array of strings
    values = [
        str(extracted_json.get("job_id", "")),
        str(extracted_json.get("title", "")),
        str(extracted_json.get("description", "")),
        str(extracted_json.get("department", "")),
        str(extracted_json.get("has_company_logo", "")),
        str(extracted_json.get("employment_type", ""))
    ]
    return np.array([values])

def predict_offer(features):
    model_path = os.path.join("model", "keras_model.keras")
    
    if tf is not None and os.path.exists(model_path):
        try:
            model = tf.keras.models.load_model(model_path)
            prediction_output = model.predict(features)
            # Assuming the model returns a 2D array like [[0.91]]
            probability = float(prediction_output[0][0])
        except Exception as e:
            # Fallback if model loading or prediction fails
            print(f"Model prediction failed: {e}")
            probability = 0.5
    else:
        # Mock probability if no model file is found
        probability = 0.85
        
    prediction = "Fraudulent" if probability >= 0.5 else "Legitimate"
    return probability, prediction

def generate_explanation(original_text: str, extracted_json: dict, prediction: str, probability: float) -> dict:
    model = get_gemini_model()
    prompt = EXPLANATION_PROMPT.format(
        text=original_text[:5000],
        extracted_json=json.dumps(extracted_json, indent=2),
        prediction=prediction,
        probability=round(probability, 2)
    )
    response = model.generate_content(prompt)
    try:
        return clean_json_response(response.text)
    except Exception as e:
        return {
            "summary": f"Could not generate explanation. Prediction is {prediction}.",
            "keywords": [],
            "explanation": ["Explanation generation failed."],
            "recommendations": ["Be cautious and verify the source."]
        }

def analyze_offer(text: str) -> dict:
    # Step 1 & 2: Gemini Feature Extraction
    extracted_json = extract_features(text)
    
    # Step 3: Feature Formatting
    features = prepare_ml_input(extracted_json)
    
    # Step 4: TensorFlow/Keras Model Prediction
    probability, prediction = predict_offer(features)
    
    # Step 5: Gemini Explainability & Keyword Extraction
    analysis = generate_explanation(text, extracted_json, prediction, probability)
    
    # Step 6: Single Structured Response
    return {
        "prediction": prediction,
        "probability": round(probability, 4),
        "extracted": extracted_json,
        "analysis": analysis
    }
