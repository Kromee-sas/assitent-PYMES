from flask import Blueprint, request, jsonify
from nlp.query_parser import QueryParser
from nlp.sql_validator import validate_sql
from database.db_connector import execute_query

main_blueprint = Blueprint("main", __name__)
query_parser = QueryParser()

@main_blueprint.route("/api/query", methods=["POST"])
def process_query():
    data = request.json
    user_query = data.get("query", "")

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    # Generate SQL Query
    sql_query = query_parser.generate_sql(user_query)

    # Validate SQL Query
    is_valid, message = validate_sql(sql_query)
    if not is_valid:
        return jsonify({"error": message}), 400

    # Execute SQL Query
    result = execute_query(sql_query)

    return jsonify({"query": sql_query, "response": result})