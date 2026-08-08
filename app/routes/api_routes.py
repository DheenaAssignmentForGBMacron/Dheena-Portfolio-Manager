from flask import (
    Blueprint,
    jsonify,
    request,
)

from app.services.asset_service import (
    search_assets,
)

api_bp = Blueprint(
    "api",
    __name__,
)


@api_bp.route("/api/assets")
def asset_api():

    search = request.args.get(
        "q",
        "",
    ).strip()

    assets = search_assets(search)

    return jsonify(
        [dict(asset) for asset in assets]
    )