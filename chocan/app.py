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
    
    # Operator Management Helpers

    TWO_LETTER_STATE_RE = re.compile(r"^[A-Za-z]{2}$")
    FIVE_DIGIT_ZIP_RE = re.compile(r"^\d{5}$")

    def _record_number(record, kind):
        if kind == "member":
            return str(record.get("number") or record.get("member_number") or "").strip()
        return str(record.get("number") or record.get("provider_number") or "").strip()

    def _validate_name_address_fields(payload, require_all=True):
        name = str(payload.get("name", "")).strip()
        street_address = str(payload.get("street_address", "")).strip()
        city = str(payload.get("city", "")).strip()
        state = str(payload.get("state", "")).strip().upper()
        zip_code = str(payload.get("zip_code", "")).strip()

        if require_all or name:
            if not name or len(name) > 25:
                return "Name must be 1-25 characters"

        if require_all or street_address:
            if not street_address or len(street_address) > 25:
                return "Street address must be 1-25 characters"

        if require_all or city:
            if not city or len(city) > 14:
                return "City must be 1-14 characters"

        if require_all or state:
            if not TWO_LETTER_STATE_RE.fullmatch(state):
                return "State must be exactly 2 letters"

        if require_all or zip_code:
            if not FIVE_DIGIT_ZIP_RE.fullmatch(zip_code):
                return "ZIP code must be exactly 5 digits"

        return None

    def _normalize_member(payload):
        number = str(payload.get("number") or payload.get("member_number") or "").strip()
        return {
            "number": number,
            "member_number": number,
            "name": str(payload.get("name", "")).strip(),
            "street_address": str(payload.get("street_address", "")).strip(),
            "city": str(payload.get("city", "")).strip(),
            "state": str(payload.get("state", "")).strip().upper(),
            "zip_code": str(payload.get("zip_code", "")).strip(),
            "status": str(payload.get("status", "active")).strip().lower(),
        }

    def _normalize_provider(payload):
        number = str(payload.get("number") or payload.get("provider_number") or "").strip()
        return {
            "number": number,
            "provider_number": number,
            "name": str(payload.get("name", "")).strip(),
            "street_address": str(payload.get("street_address", "")).strip(),
            "city": str(payload.get("city", "")).strip(),
            "state": str(payload.get("state", "")).strip().upper(),
            "zip_code": str(payload.get("zip_code", "")).strip(),
            "status": str(payload.get("status", "active")).strip().lower(),
        }

    def _apply_updates(record, payload, kind):
        fields = ["name", "street_address", "city", "state", "zip_code"]

        if kind == "member":
            fields.append("status")

        for field in fields:
            if field in payload:
                value = str(payload.get(field, "")).strip()

                if field == "state":
                    value = value.upper()

                if field == "status":
                    value = value.lower()

                record[field] = value

        return record

    # Required Member Endpoints

    @app.post("/add_member")
    def add_member():
        payload = request.get_json(silent=True) or {}
        member = _normalize_member(payload)
        number = member["number"]

        if not NINE_DIGIT_RE.fullmatch(number):
            return jsonify({"result": "Member number must be exactly 9 digits"}), 400

        field_error = _validate_name_address_fields(payload, require_all=True)
        if field_error:
            return jsonify({"result": field_error}), 400

        if member["status"] not in {"active", "suspended"}:
            return jsonify({"result": "Status must be active or suspended"}), 400

        path = data_dir / "members.json"
        members = _read_json_list(path)

        if any(_record_number(m, "member") == number for m in members):
            return jsonify({"result": "Member already exists"}), 400

        members.append(member)
        _write_json_list(path, members)

        return jsonify({"result": "Member added successfully", "member": member})

    @app.post("/update_member")
    def update_member():
        payload = request.get_json(silent=True) or {}
        number = str(payload.get("member_number") or payload.get("number") or "").strip()

        if not NINE_DIGIT_RE.fullmatch(number):
            return jsonify({"result": "Member number must be exactly 9 digits"}), 400

        if "status" in payload:
            status = str(payload.get("status", "")).strip().lower()
            if status and status not in {"active", "suspended"}:
                return jsonify({"result": "Status must be active or suspended"}), 400

        field_error = _validate_name_address_fields(payload, require_all=False)
        if field_error:
            return jsonify({"result": field_error}), 400

        path = data_dir / "members.json"
        members = _read_json_list(path)

        for member in members:
            if _record_number(member, "member") == number:
                _apply_updates(member, payload, "member")
                member["number"] = number
                member["member_number"] = number
                _write_json_list(path, members)
                return jsonify({"result": "Member updated successfully", "member": member})

        return jsonify({"result": "Member not found"}), 404

    @app.post("/delete_member")
    def delete_member():
        payload = request.get_json(silent=True) or {}
        number = str(payload.get("member_number") or payload.get("number") or "").strip()

        if not NINE_DIGIT_RE.fullmatch(number):
            return jsonify({"result": "Member number must be exactly 9 digits"}), 400

        path = data_dir / "members.json"
        members = _read_json_list(path)
        new_members = [m for m in members if _record_number(m, "member") != number]

        if len(new_members) == len(members):
            return jsonify({"result": "Member not found"}), 404

        _write_json_list(path, new_members)

        return jsonify({"result": "Member deleted successfully"})

    # Required Provider Endpoints

    @app.post("/add_provider")
    def add_provider():
        payload = request.get_json(silent=True) or {}
        provider = _normalize_provider(payload)
        number = provider["number"]

        if not NINE_DIGIT_RE.fullmatch(number):
            return jsonify({"result": "Provider number must be exactly 9 digits"}), 400

        field_error = _validate_name_address_fields(payload, require_all=True)
        if field_error:
            return jsonify({"result": field_error}), 400

        path = data_dir / "providers.json"
        providers = _read_json_list(path)

        if any(_record_number(p, "provider") == number for p in providers):
            return jsonify({"result": "Provider already exists"}), 400

        providers.append(provider)
        _write_json_list(path, providers)

        return jsonify({"result": "Provider added successfully", "provider": provider})

    @app.post("/update_provider")
    def update_provider():
        payload = request.get_json(silent=True) or {}
        number = str(payload.get("provider_number") or payload.get("number") or "").strip()

        if not NINE_DIGIT_RE.fullmatch(number):
            return jsonify({"result": "Provider number must be exactly 9 digits"}), 400

        field_error = _validate_name_address_fields(payload, require_all=False)
        if field_error:
            return jsonify({"result": field_error}), 400

        path = data_dir / "providers.json"
        providers = _read_json_list(path)

        for provider in providers:
            if _record_number(provider, "provider") == number:
                _apply_updates(provider, payload, "provider")
                provider["number"] = number
                provider["provider_number"] = number
                _write_json_list(path, providers)
                return jsonify({"result": "Provider updated successfully", "provider": provider})

        return jsonify({"result": "Provider not found"}), 404

    @app.post("/delete_provider")
    def delete_provider():
        payload = request.get_json(silent=True) or {}
        number = str(payload.get("provider_number") or payload.get("number") or "").strip()

        if not NINE_DIGIT_RE.fullmatch(number):
            return jsonify({"result": "Provider number must be exactly 9 digits"}), 400

        path = data_dir / "providers.json"
        providers = _read_json_list(path)
        new_providers = [p for p in providers if _record_number(p, "provider") != number]

        if len(new_providers) == len(providers):
            return jsonify({"result": "Provider not found"}), 404

        _write_json_list(path, new_providers)

        return jsonify({"result": "Provider deleted successfully"})

    # =========================
    # List Routes for Frontend Tables
    # =========================

    @app.get("/operator/members")
    def operator_list_members():
        return jsonify({"members": _read_json_list(data_dir / "members.json")})

    @app.get("/operator/providers")
    def operator_list_providers():
        return jsonify({"providers": _read_json_list(data_dir / "providers.json")})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
