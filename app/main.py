from flask import Flask, jsonify, render_template, request
from uuid import uuid4
import os
import json
import tempfile
import logging

from app.database import init_db, get_request, save_request
from app.analyzer import analyze

app = Flask(__name__)

# Initialize database on startup
init_db()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.errorhandler(404)
def not_found(e):
    """Custom 404 page."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    """Custom 500 page."""
    logger.error(f"Server error: {e}")
    return render_template("500.html"), 500


@app.route("/sample-csv")
def sample_csv():
    """Serve the sample CSV file for download."""
    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "tests", "fixtures", "valid_basic.csv"
    )
    sample_path = os.path.normpath(sample_path)
    if not os.path.exists(sample_path):
        return jsonify({"error": "Sample file not found"}), 404
    with open(sample_path, "r", encoding="utf-8") as f:
        content = f.read()
    response = app.response_class(response=content, status=200, mimetype="text/csv")
    response.headers["Content-Disposition"] = 'attachment; filename="datacheck-sample.csv"'
    return response


@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/")
def index():
    """Serve the service request form."""
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze_request():
    """Handle CSV upload and analysis."""
    logger.info("Received CSV analysis request")
    
    # Extract form fields
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    service = request.form.get("service", "").strip()
    description = request.form.get("description", "").strip()
    
    # Validate required fields
    if not name:
        logger.warning("Analysis request failed: missing name")
        return jsonify({"error": "Name is required"}), 400
    if not email:
        logger.warning("Analysis request failed: missing email")
        return jsonify({"error": "Email is required"}), 400
    if not service:
        logger.warning("Analysis request failed: missing service selection")
        return jsonify({"error": "Service selection is required"}), 400
    
    # Validate email format (basic check)
    if "@" not in email or "." not in email:
        logger.warning("Analysis request failed: invalid email format")
        return jsonify({"error": "Invalid email format"}), 400
    
    # Check for file upload
    if "csv_file" not in request.files:
        logger.warning("Analysis request failed: no file uploaded")
        return jsonify({"error": "CSV file is required"}), 400
    
    file = request.files["csv_file"]
    if file.filename == "":
        logger.warning("Analysis request failed: empty filename")
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file extension
    if not file.filename.lower().endswith(".csv"):
        logger.warning(f"Analysis request failed: invalid file type - {file.filename}")
        return jsonify({"error": "Only CSV files are accepted"}), 400
    
    # Save file temporarily and analyze
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        temp_path = tmp.name
        file.save(temp_path)
    
    try:
        file_size = os.path.getsize(temp_path)
        
        logger.info(f"Analyzing CSV: {file.filename}, size: {file_size} bytes")
        
        # Run analysis
        try:
            result = analyze(temp_path, file_size=file_size)
        except ValueError as e:
            logger.warning(f"Analysis request failed: {str(e)}")
            return jsonify({"error": str(e)}), 400
        
        # Save to database
        request_id = str(uuid4())
        column_info = result["column_analysis"]
        
        saved = save_request(
            request_id=request_id,
            name=name,
            email=email,
            service_selected=service,
            description=description,
            original_filename=file.filename,
            total_rows=result["total_rows"],
            total_columns=result["total_columns"],
            duplicate_rows=result["duplicate_rows"],
            column_info=json.dumps(column_info)
        )
        
        if not saved:
            logger.error(f"Analysis request {request_id} failed: database save error")
            return jsonify({"error": "Failed to save request"}), 500
        
        logger.info(f"Analysis request {request_id} completed successfully")
        
        return jsonify({
            "request_id": request_id,
            "status": "success",
            "analysis": {
                "filename": file.filename,
                "total_rows": result["total_rows"],
                "total_columns": result["total_columns"],
                "duplicate_rows": result["duplicate_rows"],
                "columns": result["column_analysis"]
            },
            "download_url": f"/api/download/{request_id}"
        })
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.debug(f"Temporary file cleaned up: {temp_path}")


@app.route("/api/download/<request_id>")
def download_report(request_id):
    """Download analysis report as JSON."""
    request_data = get_request(request_id)
    
    if not request_data:
        return jsonify({"error": "Request not found"}), 404
    
    # Parse column_info from string to dict if needed
    column_info = request_data["column_info"]
    if isinstance(column_info, str):
        try:
            column_info = json.loads(column_info)
        except Exception:
            column_info = []
    
    # Format report
    report = {
        "request_id": request_data["id"],
        "name": request_data["name"],
        "email": request_data["email"],
        "service_selected": request_data["service_selected"],
        "description": request_data["description"],
        "original_filename": request_data["original_filename"],
        "total_rows": request_data["total_rows"],
        "total_columns": request_data["total_columns"],
        "duplicate_rows": request_data["duplicate_rows"],
        "column_analysis": column_info,
        "created_at": str(request_data["created_at"])
    }

    filename = f"datacheck-report-{request_id[:8]}.json"
    response = app.response_class(
        response=json.dumps(report, indent=2),
        status=200,
        mimetype="application/json"
    )
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

