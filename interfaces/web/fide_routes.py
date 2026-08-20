"""
FIDE Management Routes.
Handles admin UI for importing, searching, and verifying FIDE data.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from application.fide_import_service import FideImportService
from application.fide_search_service import FideSearchService
from application.verification_service import VerificationService
from infrastructure.repositories import FideImportRepository
from interfaces.web.decorators import role_required

fide_bp = Blueprint("fide", __name__)

# ── Admin FIDE Management ──

@fide_bp.route("/admin/fide")
@login_required
@role_required('admin')
def fide_dashboard():
    """Main FIDE management dashboard."""
    # Get latest imports
    imports = FideImportRepository.get_all() if hasattr(FideImportRepository, 'get_all') else []
    pending_verifications = VerificationService.get_pending_requests()
    
    return render_template(
        "admin/fide_dashboard.html",
        imports=imports,
        pending_verifications=pending_verifications
    )

@fide_bp.route("/admin/fide/import", methods=["POST"])
@login_required
@role_required('admin')
def trigger_import():
    """Triggers the FIDE XML import process."""
    try:
        result = FideImportService.run_import()
        if result.get("status") == "success":
            flash(f"ایمپورت با موفقیت انجام شد. (پردازش شده: {result.get('processed')})", "success")
        elif result.get("status") == "skipped":
            flash("این ماه قبلاً ایمپورت شده است.", "info")
        else:
            flash(f"خطا در ایمپورت: {result.get('message')}", "error")
    except Exception as e:
        flash(f"خطای غیرمنتظره: {str(e)}", "error")
        
    return redirect(url_for("fide.fide_dashboard"))

@fide_bp.route("/admin/fide/search")
@login_required
@role_required('admin')
def search():
    """API endpoint for searching local FIDE players."""
    query = request.args.get("q", "")
    federation = request.args.get("federation", "IRI") # Default to IRI
    
    if not query:
        return jsonify([])
        
    results = FideSearchService.search(query, federation)
    return jsonify(results)

@fide_bp.route("/admin/fide/verifications")
@login_required
@role_required('admin')
def verifications_list():
    """View all pending verification requests."""
    pending = VerificationService.get_pending_requests()
    return render_template("admin/verifications.html", pending=pending)

@fide_bp.route("/admin/fide/verifications/<int:req_id>/approve", methods=["POST"])
@login_required
@role_required('admin')
def approve_verification(req_id):
    """Approve a verification request."""
    try:
        VerificationService.approve_request(req_id, current_user.id)
        flash("درخواست تأیید شد و هویت بازیکن باز شد.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("fide.verifications_list"))

@fide_bp.route("/admin/fide/verifications/<int:req_id>/reject", methods=["POST"])
@login_required
@role_required('admin')
def reject_verification(req_id):
    """Reject a verification request."""
    reason = request.form.get("reason", "")
    try:
        VerificationService.reject_request(req_id, current_user.id, reason)
        flash("درخواست رد شد.", "info")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("fide.verifications_list"))