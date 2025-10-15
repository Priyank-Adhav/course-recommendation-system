from flask import Blueprint, request, jsonify
import requests
import os

recommendation_service = Blueprint("recommendation_service", __name__)

RECOMMENDER_API_URL = os.getenv("RECOMMENDER_API_URL", "http://localhost:8000/recommend")

@recommendation_service.route("/recommendations", methods=["GET"])
def get_recommendations():
    query = request.args.get("query")
    top_k = request.args.get("top_k", 10)

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        response = requests.get(RECOMMENDER_API_URL, params={"query": query, "top_k": top_k})
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch recommendations: {str(e)}"}), 500
