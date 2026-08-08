from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.services.asset_service import (
    add_asset,
    get_assets,
    get_asset_summary,
)


assets_bp = Blueprint("assets", __name__)


# --------------------------------------------------
# Assets List
# --------------------------------------------------

@assets_bp.route("/assets")
def assets():

    assets = get_assets()

    summary = get_asset_summary()

    return render_template(
        "assets.html",
        assets=assets,
        summary=summary,
    )


# --------------------------------------------------
# Add Asset
# --------------------------------------------------

@assets_bp.route(
    "/add-asset",
    methods=["GET", "POST"],
)
def add_asset_page():

    if request.method == "GET":

        return render_template(
            "add_asset.html"
        )

    add_asset(
        symbol=request.form["symbol"].upper(),
        name=request.form["name"],
        asset_class=request.form["asset_class"],
        exchange=request.form["exchange"],
    )

    flash(
        "Asset added successfully.",
        "success",
    )

    return redirect(
        url_for("assets.assets")
    )
