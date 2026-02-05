from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
# Initialize Groq LLaMA 3 client
groq_client = Groq(
    api_key=os.environ.get("API_KEY")# Replace with your key
)
def generate_llm_advisory(disease_name, confidence):
    """
    Generates structured advisory using LLaMA 3
    """

    # Risk level based on confidence
    if confidence > 0.9:
        risk_level = "High"
    elif confidence > 0.7:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    prompt = f"""
    You are a professional agricultural expert.

    A plant disease detection system predicted the following:

    Disease: {disease_name}
    Prediction Confidence: {round(confidence * 100, 2)}%
    Risk Level: {risk_level}

    Generate a structured advisory in EXACTLY the following format:

    1. Disease Explanation:
    (Short and simple explanation in 2-3 sentences)

    2. Immediate Actions:
    - point
    - point
    - point

    3. Organic Treatment Options:
    - point
    - point
    - point

    4. Chemical Treatment Options:
    - point
    - point
    - point

    5. Prevention Strategies:
    - point
    - point
    - point

    6. Severity Level Explanation:
    - point
    - point

    7. Safety Disclaimer:
    (Always advise consulting a local agricultural expert before chemical treatment.)

    Important Rules:
    - Use '-' for bullet points.
    - Keep language farmer-friendly.
    - Do NOT provide extreme pesticide dosage.
    - Do NOT leave any section empty.
    """


    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Rocks LLaMA 3 Instant
            messages=[
                {"role": "system", "content": "You are a professional agricultural advisor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"LLM generation error: {str(e)}"
