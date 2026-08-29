"""
CSV Import Service for Players.

Handles CSV parsing, validation, and preview for player bulk imports.
"""
import csv
import io
import uuid
import json
from typing import List, Dict, Tuple

from app.extensions import db

from infrastructure.models.temp import TempImportDataModel


class CsvImportError(Exception):
    """Raised when CSV import fails."""
    pass


class PlayerCsvImportService:
    """Handles CSV import workflow for players."""

    VALID_TITLES = ["", "GM", "IM", "FM", "CM", "WGM", "WIM", "WFM", "WCM"]
    VALID_GENDERS = ("M", "F")
    REQUIRED_FIELDS = ("first_name", "last_name")

    @staticmethod
    def parse_csv_file(file) -> Tuple[List[Dict], List[str]]:
        """
        Parse uploaded CSV file and return validated player data.

        Returns:
            Tuple of (players_data, errors)
        """
        if not file:
            raise CsvImportError("فایلی انتخاب نشده")

        filename = file.filename.lower()
        if not filename.endswith(".csv"):
            raise CsvImportError("فقط فایل CSV پشتیبانی می‌شود")

        try:
            content = file.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                file.seek(0)
                content = file.read().decode("windows-1256")
            except Exception:
                raise CsvImportError("خطا در خواندن فایل. لطفاً فایل UTF-8 آپلود کنید")

        reader = csv.DictReader(io.StringIO(content))

        players_data = []
        errors = []
        row_num = 0

        for row in reader:
            row_num += 1

            clean_row = {}
            for key, value in row.items():
                if key:
                    clean_key = key.strip().lower().replace(" ", "_")
                    clean_row[clean_key] = (value or "").strip()

            first_name = clean_row.get("first_name", "").strip()
            last_name = clean_row.get("last_name", "").strip()

            if not first_name and not last_name:
                continue

            if not first_name or not last_name:
                errors.append(f"ردیف {row_num}: نام یا نام خانوادگی خالی است")
                continue

            rating = 0
            rating_str = clean_row.get("rating", "0").strip()
            try:
                rating = int(rating_str) if rating_str else 0
            except ValueError:
                rating = 0

            k_factor = 20
            k_str = clean_row.get("k_factor", "20").strip()
            try:
                k_factor = int(k_str) if k_str else 20
            except ValueError:
                k_factor = 20

            player_info = {
                "row": row_num,
                "first_name": first_name,
                "last_name": last_name,
                "rating": rating,
                "fide_id": clean_row.get("fide_id", "").strip(),
                "federation": clean_row.get("federation", "IRI").strip() or "IRI",
                "gender": clean_row.get("gender", "M").strip().upper() or "M",
                "birth_date": clean_row.get("birth_date", "").strip(),
                "fide_title": clean_row.get("fide_title", "").strip().upper(),
                "k_factor": k_factor,
                "age_category": clean_row.get("age_category", "").strip(),
                "custom_category": clean_row.get("custom_category", "").strip(),
            }

            if player_info["gender"] not in ("M", "F"):
                player_info["gender"] = "M"

            if player_info["fide_title"] not in PlayerCsvImportService.VALID_TITLES:
                player_info["fide_title"] = ""

            players_data.append(player_info)

        if not players_data and not errors:
            raise CsvImportError("فایل خالی است یا فرمت آن اشتباه است")

        return players_data, errors

    @staticmethod
    def store_preview(players_data: List[Dict]) -> str:
        """
        Store preview data in temporary storage.

        Returns:
            Session key for the stored preview.
        """
        # Replace any abandoned previous preview for this session
        from flask import session
        old_key = session.get("csv_import_key")
        if old_key:
            TempImportDataModel.query.filter_by(session_key=old_key).delete()

        temp_record = TempImportDataModel(
            session_key=str(uuid.uuid4()),
            data_json=json.dumps(players_data, ensure_ascii=False)
        )
        db.session.add(temp_record)
        db.session.commit()
        session["csv_import_key"] = temp_record.session_key

        return temp_record.session_key

    @staticmethod
    def get_preview() -> Tuple[List[Dict], str]:
        """
        Retrieve preview data from temporary storage.

        Returns:
            Tuple of (players_data, import_key)

        Raises:
            CsvImportError if no valid preview data found.
        """
        from flask import session
        import_key = session.get("csv_import_key")
        if not import_key:
            raise CsvImportError("داده‌های Import یافت نشد یا منقضی شده است.")

        temp_record = TempImportDataModel.query.filter_by(session_key=import_key).first()
        if not temp_record:
            raise CsvImportError("داده‌های Import منقضی شده است.")

        players_data = json.loads(temp_record.data_json)
        return players_data, import_key

    @staticmethod
    def clear_preview(import_key: str) -> None:
        """Clear preview data after confirmation."""
        from flask import session
        TempImportDataModel.query.filter_by(session_key=import_key).delete()
        db.session.commit()
        session.pop("csv_import_key", None)

    @staticmethod
    def create_players(tournament, players_data: List[Dict]) -> Tuple[int, List[str]]:
        """
        Create players from preview data.

        Returns:
            Tuple of (added_count, errors)
        """
        from application.player.participant_management import ParticipantManagement

        added = 0
        errors = []

        for p in players_data:
            try:
                form_data = {
                    "first_name": p["first_name"],
                    "last_name": p["last_name"],
                    "rating": str(p.get("rating", 0)),
                    "fide_id": p.get("fide_id", ""),
                    "federation": p.get("federation", "IRI"),
                    "gender": p.get("gender", "M"),
                    "birth_date": p.get("birth_date", ""),
                    "fide_title": p.get("fide_title", ""),
                    "k_factor": str(p.get("k_factor", 20)),
                    "age_category": p.get("age_category", ""),
                    "custom_category": p.get("custom_category", ""),
                }

                ParticipantManagement.create(tournament, form_data)
                added += 1

            except Exception as e:
                errors.append(f"{p['first_name']} {p['last_name']}: {str(e)}")

        return added, errors