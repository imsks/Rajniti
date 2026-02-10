"""
API Routes for Rajniti — Politician-centric design.

All election/party/constituency data is embedded in the Politician model,
so every route revolves around politicians.
"""

import logging
from flask import Blueprint, jsonify, request

from app.controllers.politician_controller import PoliticianController
from app.core.middleware import rate_limit, log_request, validate_pagination, RequestValidator
from app.core.exceptions import RajnitiError, ValidationError, NotFoundError
from app.core.cache import get_cache_stats

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

politician_ctrl = PoliticianController()


# ==================== UTILITY ROUTES ====================


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "Rajniti API",
        "version": "1.0.0"
    })


@api_bp.route("/cache/stats", methods=["GET"])
def cache_stats():
    """Get cache statistics"""
    stats = get_cache_stats()
    return jsonify({
        "success": True,
        "data": stats
    })


# ==================== POLITICIAN ROUTES ====================


@api_bp.route("/politicians", methods=["GET"])
@log_request
@rate_limit
def list_politicians():
    """
    List politicians with optional filters and pagination.

    Query params:
        type: MP | MLA (optional)
        page: int (default 1)
        limit: int (default 50, max 100)
    """
    try:
        election_type = request.args.get("type")
        page, limit, offset = validate_pagination()
        
        result = politician_ctrl.get_all(election_type=election_type, limit=limit)
        
        # Apply pagination
        total = len(result)
        paginated = result[offset:offset + limit]
        
        return jsonify({
            "success": True,
            "data": paginated,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        })
    except RajnitiError as e:
        return jsonify({"success": False, "error": e.message}), e.code
    except Exception as e:
        logger.exception("Unexpected error in list_politicians")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/politicians/search", methods=["GET"])
@log_request
@rate_limit
def search_politicians():
    """
    Search politicians by name, state, constituency, party.

    Query params:
        q: search query (required)
        type: MP | MLA (optional)
        state: state name filter (optional)
        party: party name filter (optional)
        page: int (default 1)
        limit: int (default 50, max 100)
        fuzzy: bool (default true) - enable fuzzy matching
    """
    try:
        query = request.args.get("q", "").strip()
        
        # Validate query
        is_valid, error_msg = RequestValidator.validate_search_query(query)
        if not is_valid:
            raise ValidationError(error_msg, field="q")
        
        # Sanitize inputs
        query = RequestValidator.sanitize_string(query, max_length=200)
        state = RequestValidator.sanitize_string(request.args.get("state", "")) if request.args.get("state") else None
        party = RequestValidator.sanitize_string(request.args.get("party", "")) if request.args.get("party") else None
        
        page, limit, offset = validate_pagination()
        use_fuzzy = request.args.get("fuzzy", "true").lower() != "false"

        result = politician_ctrl.search(
            query=query,
            election_type=request.args.get("type"),
            state=state,
            party=party,
            limit=limit * 2,  # Get more for pagination
            use_fuzzy=use_fuzzy
        )
        
        # Apply pagination
        total = len(result)
        paginated = result[offset:offset + limit]
        
        return jsonify({
            "success": True,
            "data": paginated,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        })
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message, "field": e.field}), e.code
    except RajnitiError as e:
        return jsonify({"success": False, "error": e.message}), e.code
    except Exception as e:
        logger.exception("Unexpected error in search_politicians")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/politicians/<politician_id>", methods=["GET"])
@log_request
@rate_limit
def get_politician(politician_id):
    """Get a single politician by ID."""
    try:
        # Validate politician ID
        if not RequestValidator.validate_politician_id(politician_id):
            raise ValidationError("Invalid politician ID format", field="politician_id")
        
        politician = politician_ctrl.get_by_id(politician_id)
        if not politician:
            raise NotFoundError("Politician", politician_id)
        
        return jsonify({"success": True, "data": politician})
    except NotFoundError as e:
        return jsonify({"success": False, "error": e.message}), e.code
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message, "field": e.field}), e.code
    except RajnitiError as e:
        return jsonify({"success": False, "error": e.message}), e.code
    except Exception as e:
        logger.exception(f"Unexpected error getting politician {politician_id}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/politicians/state/<state>", methods=["GET"])
@log_request
@rate_limit
def get_politicians_by_state(state):
    """Get all politicians from a state with pagination."""
    try:
        state = RequestValidator.sanitize_string(state)
        election_type = request.args.get("type")
        page, limit, offset = validate_pagination()
        
        result = politician_ctrl.get_by_state(state, election_type=election_type)
        
        # Apply pagination
        total = len(result)
        paginated = result[offset:offset + limit]
        
        return jsonify({
            "success": True,
            "data": paginated,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        })
    except RajnitiError as e:
        return jsonify({"success": False, "error": e.message}), e.code
    except Exception as e:
        logger.exception(f"Unexpected error getting politicians by state {state}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/politicians/party/<party>", methods=["GET"])
@log_request
@rate_limit
def get_politicians_by_party(party):
    """Get all politicians from a party with pagination."""
    try:
        party = RequestValidator.sanitize_string(party)
        election_type = request.args.get("type")
        page, limit, offset = validate_pagination()
        
        result = politician_ctrl.get_by_party(party, election_type=election_type)
        
        # Apply pagination
        total = len(result)
        paginated = result[offset:offset + limit]
        
        return jsonify({
            "success": True,
            "data": paginated,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        })
    except RajnitiError as e:
        return jsonify({"success": False, "error": e.message}), e.code
    except Exception as e:
        logger.exception(f"Unexpected error getting politicians by party {party}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


# ==================== AGGREGATION ROUTES ====================


@api_bp.route("/stats", methods=["GET"])
@log_request
def get_stats():
    """Get summary statistics."""
    try:
        election_type = request.args.get("type")
        result = politician_ctrl.get_stats(election_type=election_type)
        return jsonify({"success": True, "data": result})
    except RajnitiError as e:
        return jsonify({"success": False, "error": e.message}), e.code
    except Exception as e:
        logger.exception("Unexpected error getting stats")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/states", methods=["GET"])
@log_request
def get_states():
    """Get list of unique states."""
    try:
        election_type = request.args.get("type")
        states = politician_ctrl.get_states(election_type=election_type)
        return jsonify({"success": True, "data": {"states": states, "total": len(states)}})
    except RajnitiError as e:
        return jsonify({"success": False, "error": e.message}), e.code
    except Exception as e:
        logger.exception("Unexpected error getting states")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/parties", methods=["GET"])
@log_request
def get_parties():
    """Get list of unique parties."""
    try:
        election_type = request.args.get("type")
        parties = politician_ctrl.get_parties(election_type=election_type)
        return jsonify({"success": True, "data": {"parties": parties, "total": len(parties)}})
    except RajnitiError as e:
        return jsonify({"success": False, "error": e.message}), e.code
    except Exception as e:
        logger.exception("Unexpected error getting parties")
        return jsonify({"success": False, "error": "Internal server error"}), 500


# ==================== QUESTIONS ROUTES (Vector DB) ====================


_questions_service = None


def _get_questions_service():
    """Lazy init to avoid import errors when ChromaDB is not installed."""
    global _questions_service
    if _questions_service is None:
        try:
            from app.services.questions_service import QuestionsService
            _questions_service = QuestionsService()
        except Exception as e:
            logger.warning("QuestionsService unavailable: %s", e)
            return None
    return _questions_service


@api_bp.route("/questions", methods=["GET"])
def get_predefined_questions():
    """Get predefined questions."""
    try:
        from app.schemas.questions import PREDEFINED_QUESTIONS
        return jsonify({
            "success": True,
            "data": {"questions": PREDEFINED_QUESTIONS, "total": len(PREDEFINED_QUESTIONS)},
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/questions/ask", methods=["POST"])
@log_request
@rate_limit
def ask_question():
    """Ask a question — semantic search over politician data."""
    try:
        data = request.get_json()
        if not data or not data.get("question"):
            raise ValidationError("Question is required", field="question")

        # Validate question
        question = RequestValidator.sanitize_string(data["question"], max_length=500)
        is_valid, error_msg = RequestValidator.validate_search_query(question)
        if not is_valid:
            raise ValidationError(error_msg, field="question")

        qs = _get_questions_service()
        if not qs:
            return jsonify({
                "success": False,
                "error": "Questions service unavailable. Vector DB may not be configured.",
            }), 503

        result = qs.answer_question(
            question=question,
            n_results=data.get("n_results", 5),
        )
        return jsonify(result)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message, "field": e.field}), e.code
    except Exception as e:
        logger.exception("Unexpected error in ask_question")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/questions/<question_id>/answer", methods=["GET"])
def answer_predefined_question(question_id):
    """Answer a predefined question by ID."""
    try:
        qs = _get_questions_service()
        if not qs:
            return jsonify({
                "success": False,
                "error": "Questions service unavailable.",
            }), 503

        n_results = request.args.get("n_results", default=5, type=int)
        result = qs.answer_predefined_question(
            question_id=questiINFO ====================


@api_bp.route("/", methods=["GET"])
def api_root():
    """API root with available endpoints."""
    return jsonify({
        "success": True,
        "message": "Welcome to Rajniti API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/api/v1/health",
            "cache_stats": "/api/v1/cache/stats",
            "politicians": "/api/v1/politicians",
            "search": "/api/v1/politicians/search?q=<query>",
            "by_state": "/api/v1/politicians/state/<state>",
            "by_party": "/api/v1/politicians/party/<party>",
            "stats": "/api/v1/stats",
            "states": "/api/v1/states",
            "parties": "/api/v1/parties",
            "questions": "/api/v1/questions",
            "ask": "/api/v1/questions/ask (POST)
    from app.core.database import check_db_health

    db_ok = check_db_health()
    return jsonify({
        "success": True,
        "message": "Rajniti API is healthy",
        "version": "2.0.0",
        "database": {
            "connected": db_ok,
            "status": "healthy" if db_ok else "not configured",
        },
    })
