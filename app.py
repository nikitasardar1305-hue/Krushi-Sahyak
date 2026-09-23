from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory
)

from pathlib import Path

from database import (
    get_crops,
    get_markets,
    get_historical_data,
    get_current_market,
    calculate_statistics,
    calculate_trend,
    calculate_prediction,
    get_advisory,
    get_alerts,
    get_experts,
    get_schemes,
    get_input_shops,
    analyze_crop_image,
    load_demo_data
)


# ---------------------------------------------------------
# APP CONFIGURATION
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__)


# ---------------------------------------------------------
# FRONTEND
# ---------------------------------------------------------

@app.route("/")
def home():
    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/style.css")
def stylesheet():
    return send_from_directory(
        FRONTEND_DIR,
        "style.css"
    )


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.route("/api/health")
def health():

    return jsonify({
        "status": "online",
        "application": "Krushi Sahayak",
        "data_mode": "DEMO",
        "message": "Krushi Sahayak backend is running."
    })


# ---------------------------------------------------------
# APPLICATION INFORMATION
# ---------------------------------------------------------

@app.route("/api/info")
def application_info():

    data = load_demo_data()

    return jsonify(data)


# ---------------------------------------------------------
# CROPS
# ---------------------------------------------------------

@app.route("/api/crops")
def crops():

    return jsonify({
        "success": True,
        "crops": get_crops()
    })


# ---------------------------------------------------------
# MARKETS
# ---------------------------------------------------------

@app.route("/api/markets")
def markets():

    commodity = request.args.get("commodity")

    return jsonify({
        "success": True,
        "commodity": commodity,
        "markets": get_markets(commodity)
    })


# ---------------------------------------------------------
# HISTORICAL MARKET DATA
# ---------------------------------------------------------

@app.route("/api/history")
def history():

    commodity = request.args.get("commodity")
    market = request.args.get("market")

    if not commodity or not market:
        return jsonify({
            "success": False,
            "error": "commodity and market are required."
        }), 400

    data = get_historical_data(
        commodity,
        market
    )

    if not data:
        return jsonify({
            "success": False,
            "error": "No market data found."
        }), 404

    statistics = calculate_statistics(data)
    trend = calculate_trend(data)

    return jsonify({
        "success": True,
        "commodity": commodity,
        "market": market,
        "data": data,
        "statistics": statistics,
        "trend": trend,
        "data_mode": "DEMO"
    })


# ---------------------------------------------------------
# CURRENT MARKET
# ---------------------------------------------------------

@app.route("/api/current")
def current_market():

    commodity = request.args.get("commodity")
    market = request.args.get("market")

    if not commodity or not market:
        return jsonify({
            "success": False,
            "error": "commodity and market are required."
        }), 400

    current = get_current_market(
        commodity,
        market
    )

    if not current:
        return jsonify({
            "success": False,
            "error": "No current market data found."
        }), 404

    return jsonify({
        "success": True,
        "current": current
    })


# ---------------------------------------------------------
# AI-ASSISTED MARKET OUTLOOK
# ---------------------------------------------------------

@app.route("/api/prediction")
def prediction():

    commodity = request.args.get("commodity")
    market = request.args.get("market")

    if not commodity or not market:
        return jsonify({
            "success": False,
            "error": "commodity and market are required."
        }), 400

    result = calculate_prediction(
        commodity,
        market
    )

    return jsonify({
        "success": True,
        "commodity": commodity,
        "market": market,
        "prediction": result
    })


# ---------------------------------------------------------
# MARKET INTELLIGENCE
# ---------------------------------------------------------

@app.route("/api/intelligence")
def intelligence():

    commodity = request.args.get("commodity")
    market = request.args.get("market")

    if not commodity or not market:
        return jsonify({
            "success": False,
            "error": "commodity and market are required."
        }), 400

    historical = get_historical_data(
        commodity,
        market
    )

    if not historical:
        return jsonify({
            "success": False,
            "error": "No market data found."
        }), 404

    current = get_current_market(
        commodity,
        market
    )

    statistics = calculate_statistics(
        historical
    )

    trend = calculate_trend(
        historical
    )

    outlook = calculate_prediction(
        commodity,
        market
    )

    return jsonify({
        "success": True,

        "commodity": commodity,

        "market": market,

        "past": {
            "history": historical,
            "statistics": statistics,
            "trend": trend
        },

        "present": {
            "current": current
        },

        "future": {
            "outlook": outlook
        },

        "data_mode": "DEMO",

        "disclaimer": (
            "Historical and current values shown in this prototype "
            "come from the supplied dataset. The AI-assisted outlook "
            "is an estimate and does not guarantee future prices, "
            "profits or income."
        )
    })


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/api/dashboard")
def dashboard():

    location = request.args.get(
        "location",
        "Pune"
    )

    alerts = get_alerts(location)

    return jsonify({
        "success": True,
        "location": location,
        "alerts": alerts,
        "alert_count": len(alerts),
        "data_mode": "DEMO"
    })


# ---------------------------------------------------------
# CROP ADVISORY
# ---------------------------------------------------------

@app.route("/api/advisory")
def advisory():

    crop = request.args.get("crop")

    if not crop:
        return jsonify({
            "success": False,
            "error": "crop is required."
        }), 400

    return jsonify({
        "success": True,
        "advisory": get_advisory(crop)
    })


# ---------------------------------------------------------
# EXPERTS
# ---------------------------------------------------------

@app.route("/api/experts")
def experts():

    location = request.args.get(
        "location",
        "Pune"
    )

    return jsonify({
        "success": True,
        "location": location,
        "experts": get_experts(location),
        "data_mode": "DEMO"
    })


# ---------------------------------------------------------
# AGRICULTURAL ALERTS
# ---------------------------------------------------------

@app.route("/api/alerts")
def alerts():

    location = request.args.get(
        "location"
    )

    return jsonify({
        "success": True,
        "alerts": get_alerts(location)
    })


# ---------------------------------------------------------
# GOVERNMENT SCHEMES
# ---------------------------------------------------------

@app.route("/api/schemes")
def schemes():

    return jsonify({
        "success": True,
        "schemes": get_schemes()
    })


# ---------------------------------------------------------
# AGRICULTURAL INPUT / SERVICE DIRECTORY
# ---------------------------------------------------------

@app.route("/api/input-shops")
def input_shops():

    location = request.args.get(
        "location",
        "Pune"
    )

    return jsonify({
        "success": True,
        "location": location,
        "shops": get_input_shops(location),
        "data_mode": "DEMO"
    })


# ---------------------------------------------------------
# CROP IMAGE ANALYSIS
# ---------------------------------------------------------

@app.route("/api/analyze-image", methods=["POST"])
def analyze_image():

    if "image" not in request.files:

        return jsonify({
            "success": False,
            "error": "No image uploaded."
        }), 400

    image = request.files["image"]

    if not image.filename:

        return jsonify({
            "success": False,
            "error": "The uploaded image has no filename."
        }), 400

    result = analyze_crop_image(
        image.filename
    )

    return jsonify({
        "success": True,
        "analysis": result
    })


# ---------------------------------------------------------
# OPTIONAL TRADE INFORMATION ENDPOINT
# ---------------------------------------------------------

@app.route("/api/trade")
def trade():

    commodity = request.args.get(
        "commodity",
        "Agricultural commodities"
    )

    return jsonify({
        "success": True,
        "commodity": commodity,
        "status": "REFERENCE",
        "message": (
            "Import/export information should be connected "
            "to verified government trade-data sources before "
            "being presented as live information."
        ),
        "data_mode": "PROTOTYPE"
    })


# ---------------------------------------------------------
# ERROR HANDLERS
# ---------------------------------------------------------

@app.errorhandler(404)
def not_found(error):

    if request.path.startswith("/api/"):

        return jsonify({
            "success": False,
            "error": "API endpoint not found."
        }), 404

    return error


@app.errorhandler(500)
def server_error(error):

    if request.path.startswith("/api/"):

        return jsonify({
            "success": False,
            "error": "Internal server error."
        }), 500

    return error


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("        KRUSHI SAHAYAK")
    print("        Smarter Decisions. Stronger Farms.")
    print("=" * 60)
    print()
    print("Backend running at:")
    print("http://127.0.0.1:5000")
    print()
    print("Available API:")
    print("  /api/health")
    print("  /api/crops")
    print("  /api/markets")
    print("  /api/history")
    print("  /api/current")
    print("  /api/prediction")
    print("  /api/intelligence")
    print("  /api/dashboard")
    print("  /api/advisory")
    print("  /api/alerts")
    print("  /api/experts")
    print("  /api/schemes")
    print("  /api/input-shops")
    print("  /api/analyze-image")
    print()
    print("NOTE: Prototype/demo data is clearly marked.")
    print("=" * 60)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )