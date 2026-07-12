"""HTTP routes (API v1).

The routes layer sits above the modules and may wire any module facade. It is
the composition root for cross-module flows (e.g. combining `reps` + `promises`
DTOs in a response), keeping the modules themselves free of sibling imports.
"""

from __future__ import annotations

from flask import Blueprint, jsonify

from app.promises import PromisesService
from app.reps import RepsService

api_v1 = Blueprint("api_v1", __name__)

_reps = RepsService()
_promises = PromisesService()


@api_v1.get("/reps/<rep_id>")
def get_rep(rep_id: str):
    rep = _reps.get_representative(rep_id)
    return jsonify(rep.model_dump())


@api_v1.get("/reps/<rep_id>/promises")
def get_rep_promises(rep_id: str):
    promises = _promises.list_promises(rep_id)
    return jsonify([p.model_dump() for p in promises])
