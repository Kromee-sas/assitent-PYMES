from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.nlp.query_parser import QueryParser
from app.nlp.sql_validator import validate_sql
from app.database.db_connector import execute_query

nlp_blueprint = Blueprint("nlp", __name__)
query_parser = QueryParser()

@nlp_blueprint.route("/api/query", methods=["POST"])
@jwt_required()
def process_query():
    identity = get_jwt_identity()
    company_id = identity.get("company_id")

    data = request.json
    user_query = data.get("query", "")

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    # Generate SQL Query with company scope
    sql_query = query_parser.generate_sql(user_query, company_id=company_id)

    # Validate SQL Query
    is_valid, message = validate_sql(sql_query)
    if not is_valid:
        return jsonify({"error": message}), 400

    # Execute SQL Query
    result = execute_query(sql_query)

    return jsonify({"query": sql_query, "response": result})