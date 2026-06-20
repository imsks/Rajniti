"""Browser scrape and source-sync HTTP routes."""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from app.browser.scraper import run_scrape_agent
from app.services import PoliticianService
from app.sources.myneta_resolve import (
    build_resolve_instructions,
    build_search_url,
    parse_resolve_result,
)
from app.sources.orchestrator import SourceOrchestrator

logger = logging.getLogger(__name__)

scrape_bp = Blueprint("scrape", __name__, url_prefix="/api/v1")

_politician_service = PoliticianService()
_orchestrator = SourceOrchestrator(politician_service=_politician_service)


def _json_body() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {}
    return data


@scrape_bp.route("/scrape", methods=["POST"])
def scrape_website():
    """Generic browser scrape — locals-style plain-text extraction."""
    body = _json_body()
    url = (body.get("url") or "").strip()
    if not url:
        return jsonify({"success": False, "error": "Field 'url' is required"}), 400

    instructions = body.get("instructions")
    max_steps = body.get("max_steps")

    try:
        scrape_result = run_scrape_agent(
            url,
            instructions,
            max_steps=max_steps,
        )
    except Exception as exc:
        logger.warning("Scrape agent failed for %s: %s", url, exc)
        return (
            jsonify({"success": False, "error": f"Scrape agent failed: {exc}"}),
            502,
        )

    return jsonify(
        {
            "success": True,
            "url": scrape_result.url,
            "task": scrape_result.task,
            "result": scrape_result.result,
            "steps_taken": scrape_result.steps_taken,
        }
    )


@scrape_bp.route("/scrape/myneta/resolve", methods=["POST"])
def resolve_myneta():
    """Find MyNeta candidate.php profile URL via browser agent."""
    body = _json_body()
    name = (body.get("name") or "").strip()
    state = (body.get("state") or "").strip()
    constituency = (body.get("constituency") or "").strip()
    election_slug = (body.get("election_slug") or "").strip()
    max_steps = body.get("max_steps")

    missing = [
        field
        for field, value in (
            ("name", name),
            ("state", state),
            ("constituency", constituency),
            ("election_slug", election_slug),
        )
        if not value
    ]
    if missing:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing)}",
                }
            ),
            400,
        )

    search_url = build_search_url(election_slug)
    instructions = build_resolve_instructions(name, state, constituency, election_slug)

    try:
        scrape_result = run_scrape_agent(
            search_url,
            instructions,
            max_steps=max_steps,
        )
    except Exception as exc:
        logger.warning("MyNeta resolve agent failed: %s", exc)
        return (
            jsonify({"success": False, "error": f"MyNeta resolve agent failed: {exc}"}),
            502,
        )

    parsed = parse_resolve_result(scrape_result.result, election_slug)
    if not parsed.url:
        snippet = (scrape_result.result or "")[:500]
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Could not resolve MyNeta URL. Agent output: {snippet}",
                    "raw_result": parsed.raw_result,
                }
            ),
            404,
        )

    return jsonify(
        {
            "success": True,
            "url": parsed.url,
            "candidate_id": parsed.candidate_id,
            "election_slug": parsed.election_slug,
            "raw_result": parsed.raw_result,
        }
    )


@scrape_bp.route("/politicians/<politician_id>/sync-sources", methods=["POST"])
def sync_politician_sources(politician_id: str):
    """Run registered source scrapers for one politician and persist merged data."""
    politician = _politician_service.get_by_id(politician_id)
    if not politician:
        return (
            jsonify({"success": False, "error": f"Politician not found: {politician_id}"}),
            404,
        )

    body = _json_body()
    source_names = body.get("sources")
    force = bool(body.get("force", False))

    if source_names is not None and not isinstance(source_names, list):
        return (
            jsonify({"success": False, "error": "Field 'sources' must be a list of source names"}),
            400,
        )

    try:
        result = _orchestrator.sync_politician(
            politician,
            source_names=source_names,
            force=force,
        )
    except Exception as exc:
        logger.warning("Source sync failed for %s: %s", politician_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500

    updated = _politician_service.get_by_id(politician_id)
    return jsonify({"success": True, "data": {"sync": result, "politician": updated}})


@scrape_bp.route("/politicians/<politician_id>/enrich", methods=["POST"])
def enrich_politician(politician_id: str):
    """Run full agentic pipeline: source sync, LLM enrichment, citation backfill."""
    politician = _politician_service.get_by_id(politician_id)
    if not politician:
        return (
            jsonify({"success": False, "error": f"Politician not found: {politician_id}"}),
            404,
        )

    body = _json_body()
    source_names = body.get("sources")
    force = bool(body.get("force", False))
    skip_sources = bool(body.get("skip_sources", False))
    skip_citations = bool(body.get("skip_citations", False))

    if source_names is not None and not isinstance(source_names, list):
        return (
            jsonify({"success": False, "error": "Field 'sources' must be a list of source names"}),
            400,
        )

    from app.agents.politician_agent import PoliticianAgent

    agent = PoliticianAgent()
    agent.politician_service = _politician_service
    agent.source_orchestrator.politician_service = _politician_service
    agent.citation_agent.politician_service = _politician_service

    try:
        result = agent.run(
            politician_id=politician_id,
            force=force,
            source_names=source_names,
            skip_sources=skip_sources,
            skip_citations=skip_citations,
        )
    except Exception as exc:
        logger.warning("Enrichment failed for %s: %s", politician_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 502

    updated = _politician_service.get_by_id(politician_id)
    return jsonify(
        {
            "success": bool(result.get("ok")),
            "data": {"enrichment": result, "politician": updated},
        }
    )
