from pathlib import Path

from flask import Flask, jsonify, render_template, request

from modules.billing import bill_service
from modules.reports import generate_reports
from modules.validation import get_provider, get_service, provider_directory, validate_member, validate_provider
import re
import json


DATE_MM_DD_YYYY_RE = re.compile(r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])-\d{4}$")
NINE_DIGIT_RE = re.compile(r"^\d{9}$")


def create_app(*, data_dir: Path | None = None, outputs_dir: Path | None = None) -> Flask:
    app = Flask(__name__)

    base_dir = Path(__file__).resolve().parent
    data_dir = data_dir or (base_dir / "data")
    outputs_dir = outputs_dir or (base_dir / "outputs")

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/validate_member")
    def validate_member_route():
        payload = request.get_json(silent=True) or {}
        member_number = str(payload.get("member_number", "")).strip()
        if not member_number:
            return jsonify({"result": "Invalid number"}), 400
        if not NINE_DIGIT_RE.fullmatch(member_number):
            return jsonify({"result": "Invalid number"}), 400
        result = validate_member(member_number, data_dir)
        return jsonify({"result": result})

    @app.post("/validate_provider")
    def validate_provider_route():
        payload = request.get_json(silent=True) or {}
        provider_number = str(payload.get("provider_number", "")).strip()
        if not provider_number:
            return jsonify({"result": "Invalid number"}), 400
        if not NINE_DIGIT_RE.fullmatch(provider_number):
            return jsonify({"result": "Invalid number"}), 400
        result = validate_provider(provider_number, data_dir)
        if result == "Validated":
            p = get_provider(provider_number, data_dir) or {}
            return jsonify({"result": result, "provider_name": str(p.get("name", "")).strip()})
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
        date_of_service = str(payload.get("date_of_service", "")).strip()
        if not date_of_service:
            return jsonify({"result": "Invalid date of service", "record": None}), 400
        if not DATE_MM_DD_YYYY_RE.fullmatch(date_of_service):
            return jsonify({"result": "Invalid date format (MM-DD-YYYY)", "record": None}), 400

        comments = str(payload.get("comments", "") or "")
        comments = comments[:100]
        ok, msg, record = bill_service(
            provider_number=str(payload.get("provider_number", "")).strip(),
            member_number=str(payload.get("member_number", "")).strip(),
            service_code=str(payload.get("service_code", "")).strip(),
            date_of_service=date_of_service,
            comments=comments,
            data_dir=data_dir,
        )
        status = 200 if ok else 400
        return jsonify({"result": msg, "record": record}), status

    @app.get("/verify_service_code")
    def verify_service_code_route():
        service_code = str(request.args.get("service_code", "")).strip()
        if not service_code:
            return jsonify({"found": False})
        s = get_service(service_code, data_dir)
        if not s:
            return jsonify({"found": False})
        return jsonify(
            {
                "found": True,
                "service_name": str(s.get("name", "")).strip(),
                "fee": float(s.get("fee", 0) or 0),
            }
        )

    @app.get("/provider_directory")
    def provider_directory_route():
        return jsonify({"services": provider_directory(data_dir)})

    @app.post("/run_reports")
    def run_reports_route():
        outputs_dir.mkdir(parents=True, exist_ok=True)
        generated = generate_reports(data_dir=data_dir, outputs_dir=outputs_dir)
        return jsonify({"result": "OK", "generated": generated})

    @app.get("/outputs_list")
    def outputs_list_route():
        outputs_dir.mkdir(parents=True, exist_ok=True)
        files = sorted([p.name for p in outputs_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"])
        return jsonify({"files": files})

    def _read_json_list(path: Path):
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    def _write_json_list(path: Path, items):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)

    # Operator CRUD (prototype; no auth)
    @app.get("/operator/members")
    def operator_list_members():
        return jsonify({"members": _read_json_list(data_dir / "members.json")})

    @app.post("/operator/members")
    def operator_add_member():
        payload = request.get_json(silent=True) or {}
        member_number = str(payload.get("member_number", "")).strip()
        name = str(payload.get("name", "")).strip()
        status = str(payload.get("status", "active")).strip().lower()
        if not NINE_DIGIT_RE.fullmatch(member_number) or not name:
            return jsonify({"result": "Invalid input"}), 400
        if status not in {"active", "suspended"}:
            return jsonify({"result": "Invalid status"}), 400
        path = data_dir / "members.json"
        members = _read_json_list(path)
        if any(str(m.get("member_number", "")).strip() == member_number for m in members):
            return jsonify({"result": "Member already exists"}), 400
        members.append({"member_number": member_number, "name": name, "status": status})
        _write_json_list(path, members)
        return jsonify({"result": "OK"})

    @app.put("/operator/members/<member_number>")
    def operator_update_member(member_number: str):
        member_number = str(member_number).strip()
        payload = request.get_json(silent=True) or {}
        name = str(payload.get("name", "")).strip()
        status = str(payload.get("status", "")).strip().lower()
        if not NINE_DIGIT_RE.fullmatch(member_number):
            return jsonify({"result": "Invalid number"}), 400
        if status and status not in {"active", "suspended"}:
            return jsonify({"result": "Invalid status"}), 400
        path = data_dir / "members.json"
        members = _read_json_list(path)
        found = False
        for m in members:
            if str(m.get("member_number", "")).strip() == member_number:
                if name:
                    m["name"] = name
                if status:
                    m["status"] = status
                found = True
                break
        if not found:
            return jsonify({"result": "Not found"}), 404
        _write_json_list(path, members)
        return jsonify({"result": "OK"})

    @app.delete("/operator/members/<member_number>")
    def operator_delete_member(member_number: str):
        member_number = str(member_number).strip()
        if not NINE_DIGIT_RE.fullmatch(member_number):
            return jsonify({"result": "Invalid number"}), 400
        path = data_dir / "members.json"
        members = _read_json_list(path)
        new_members = [m for m in members if str(m.get("member_number", "")).strip() != member_number]
        if len(new_members) == len(members):
            return jsonify({"result": "Not found"}), 404
        _write_json_list(path, new_members)
        return jsonify({"result": "OK"})

    @app.get("/operator/providers")
    def operator_list_providers():
        return jsonify({"providers": _read_json_list(data_dir / "providers.json")})

    @app.post("/operator/providers")
    def operator_add_provider():
        payload = request.get_json(silent=True) or {}
        provider_number = str(payload.get("provider_number", "")).strip()
        name = str(payload.get("name", "")).strip()
        status = str(payload.get("status", "active")).strip().lower()
        if not NINE_DIGIT_RE.fullmatch(provider_number) or not name:
            return jsonify({"result": "Invalid input"}), 400
        if status not in {"active", "suspended"}:
            return jsonify({"result": "Invalid status"}), 400
        path = data_dir / "providers.json"
        providers = _read_json_list(path)
        if any(str(p.get("provider_number", "")).strip() == provider_number for p in providers):
            return jsonify({"result": "Provider already exists"}), 400
        providers.append({"provider_number": provider_number, "name": name, "status": status})
        _write_json_list(path, providers)
        return jsonify({"result": "OK"})

    @app.put("/operator/providers/<provider_number>")
    def operator_update_provider(provider_number: str):
        provider_number = str(provider_number).strip()
        payload = request.get_json(silent=True) or {}
        name = str(payload.get("name", "")).strip()
        status = str(payload.get("status", "")).strip().lower()
        if not NINE_DIGIT_RE.fullmatch(provider_number):
            return jsonify({"result": "Invalid number"}), 400
        if status and status not in {"active", "suspended"}:
            return jsonify({"result": "Invalid status"}), 400
        path = data_dir / "providers.json"
        providers = _read_json_list(path)
        found = False
        for p in providers:
            if str(p.get("provider_number", "")).strip() == provider_number:
                if name:
                    p["name"] = name
                if status:
                    p["status"] = status
                found = True
                break
        if not found:
            return jsonify({"result": "Not found"}), 404
        _write_json_list(path, providers)
        return jsonify({"result": "OK"})

    @app.delete("/operator/providers/<provider_number>")
    def operator_delete_provider(provider_number: str):
        provider_number = str(provider_number).strip()
        if not NINE_DIGIT_RE.fullmatch(provider_number):
            return jsonify({"result": "Invalid number"}), 400
        path = data_dir / "providers.json"
        providers = _read_json_list(path)
        new_providers = [p for p in providers if str(p.get("provider_number", "")).strip() != provider_number]
        if len(new_providers) == len(providers):
            return jsonify({"result": "Not found"}), 404
        _write_json_list(path, new_providers)
        return jsonify({"result": "OK"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
