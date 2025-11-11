from flask import Blueprint, request, jsonify
import requests
import os

recommendation_service = Blueprint("recommendation_service", __name__)

RECOMMENDER_API_URL = os.getenv("RECOMMENDER_API_URL", "http://localhost:8000")

@recommendation_service.route("/recommendations", methods=["GET"])
def get_recommendations():
    query = request.args.get("query")
    user_id = request.args.get("user_id")
    top_k = request.args.get("top_k", 10)

    try:
        if user_id:
            # Personalized recommendation (from FastAPI)
            response = requests.get(f"{RECOMMENDER_API_URL}/recommend/{user_id}")
        elif query:
            # Search-based recommendation
            response = requests.get(
                f"{RECOMMENDER_API_URL}/recommend",
                params={"query": query, "top_k": top_k},
            )
        else:
            return jsonify({"error": "Either 'query' or 'user_id' parameter is required"}), 400

        response.raise_for_status()
        return jsonify(response.json())

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch recommendations: {str(e)}"}), 500
