from flask import Flask, jsonify, render_template, request
from uuid import uuid4
import os
import tempfile

from app.database import init_db, get_request, save_request
from app.analyzer import analyze

app = Flask(__name__)

# Initialize database on startup
init_db()

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
    # Extract form fields
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    service = request.form.get("service", "").strip()
    description = request.form.get("description", "").strip()
    
    # Validate required fields
    if not name:
        return jsonify({"error": "Name is required"}), 400
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not service:
        return jsonify({"error": "Service selection is required"}), 400
    
    # Validate email format (basic check)
    if "@" not in email or "." not in email:
        return jsonify({"error": "Invalid email format"}), 400
    
    # Check for file upload
    if "csv_file" not in request.files:
        return jsonify({"error": "CSV file is required"}), 400
    
    file = request.files["csv_file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file extension
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are accepted"}), 400
    
    # Save file temporarily and analyze
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        temp_path = tmp.name
        file.save(temp_path)
    
    try:
        file_size = os.path.getsize(temp_path)
        
        # Run analysis
        result = analyze(temp_path, file_size=file_size)
        
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
            column_info=str(column_info)  # Will be JSON in full implementation
        )
        
        if not saved:
            return jsonify({"error": "Failed to save request"}), 500
        
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
            import json
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
    
    return jsonify(report)

