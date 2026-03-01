from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# ===============================
# CONFIGURATION GROQ (SÉCURISÉE)
# ===============================
#GROQ_API_KEY = os.environ.get("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")
GROQ_API_KEY = os.environ.get("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")
if not GROQ_API_KEY:
    raise ValueError("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")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


@app.route("/recommend", methods=["POST"])
def recommend_movie():
    try:
        data = request.get_json()
        mood = data.get("mood")
        language = data.get("language")
        genre = data.get("genre")

        if not mood or not language or not genre:
            return jsonify({"error": "Tous les champs sont requis"}), 400

        if not GROQ_API_KEY:
            return jsonify({"error": "Clé API GROQ non configurée sur le serveur"}), 500

        movie = get_groq_recommendation(mood, language, genre)
        return jsonify(movie)

    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500


def get_groq_recommendation(mood, language, genre):

    prompt = f"""
    Tu es un expert en cinéma.
    Recommande UN SEUL film correspondant à :

    - Humeur : {mood}
    - Langue : {language}
    - Genre : {genre}

    Réponds uniquement avec un JSON valide :
    {{
        "title": "Titre",
        "overview": "Description en français",
        "rating": "Note/10",
        "date": "Année",
        "poster_url": ""
    }}
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Tu réponds uniquement en JSON valide."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 500,
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    response.raise_for_status()

    result = response.json()
    ai_response = result["choices"][0]["message"]["content"].strip()
    ai_response = ai_response.replace("```json", "").replace("```", "").strip()

    return json.loads(ai_response)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Backend Flask en ligne",
        "groq_api_configured": bool(GROQ_API_KEY)
    })


# ===============================
# LANCEMENT LOCAL UNIQUEMENT
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)

