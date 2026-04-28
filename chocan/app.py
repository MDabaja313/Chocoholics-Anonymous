from pathlib import Path

from flask import Flask, jsonify, render_template, request

from modules.billing import bill_service
from modules.reports import generate_reports
from modules.validation import provider_directory, validate_member, validate_provider


def create_app() -> Flask:
    app = Flask(__name__)

    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    outputs_dir = base_dir / "outputs"

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/validate_member")
    def validate_member_route():
        payload = request.get_json(silent=True) or {}
        member_number = str(payload.get("member_number", "")).strip()
        if not member_number:
            return jsonify({"result": "Invalid number"}), 400
        result = validate_member(member_number, data_dir)
        return jsonify({"result": result})

    @app.post("/validate_provider")
    def validate_provider_route():
        payload = request.get_json(silent=True) or {}
        provider_number = str(payload.get("provider_number", "")).strip()
        if not provider_number:
            return jsonify({"result": "Invalid number"}), 400
        result = validate_provider(provider_number, data_dir)
        return jsonify({"result": result})

    @app.post("/bill_service")
    def bill_service_route():
        payload = request.get_json(silent=True) or {}
        if not str(payload.get("provider_number", "")).strip():
            return jsonify({"result": "Invalid number", "record": None}), 400
        if not str(payload.get("member_number", "")).strip():
            return jsonify({"result": "Invalid number", "record": None}), 400
        if not str(payload.get("service_code", "")).strip():
            return jsonify({"result": "Invalid service code", "record": None}), 400
        if not str(payload.get("date_of_service", "")).strip():
            return jsonify({"result": "Invalid date of service", "record": None}), 400
        ok, msg, record = bill_service(
            provider_number=str(payload.get("provider_number", "")).strip(),
            member_number=str(payload.get("member_number", "")).strip(),
            service_code=str(payload.get("service_code", "")).strip(),
            date_of_service=str(payload.get("date_of_service", "")).strip(),
            comments=payload.get("comments", ""),
            data_dir=data_dir,
        )
        status = 200 if ok else 400
        return jsonify({"result": msg, "record": record}), status

    @app.get("/provider_directory")
    def provider_directory_route():
        return jsonify({"services": provider_directory(data_dir)})

    @app.post("/run_reports")
    def run_reports_route():
        outputs_dir.mkdir(parents=True, exist_ok=True)
        generated = generate_reports(data_dir=data_dir, outputs_dir=outputs_dir)
        return jsonify({"result": "OK", "generated": generated})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
