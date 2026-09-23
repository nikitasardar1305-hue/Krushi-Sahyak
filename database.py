from pathlib import Path
import csv
import json
from statistics import mean, pstdev


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

MARKET_DATA_FILE = DATA_DIR / "market_data.csv"
DEMO_DATA_FILE = DATA_DIR / "demo_data.json"


# ---------------------------------------------------------
# BASIC FILE LOADERS
# ---------------------------------------------------------

def load_market_data():
    """
    Load market data from market_data.csv.
    Handles blank lines and extra spaces safely.
    """

    if not MARKET_DATA_FILE.exists():
        print(f"Market data file not found: {MARKET_DATA_FILE}")
        return []

    records = []

    try:
        with open(
            MARKET_DATA_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                # Skip completely empty rows
                if not row:
                    continue

                # Clean column names and values
                cleaned = {
                    str(key).strip(): str(value).strip()
                    for key, value in row.items()
                    if key is not None
                }

                if not cleaned.get("commodity"):
                    continue

                try:
                    record = {
                        "date": cleaned.get("date", ""),
                        "commodity": cleaned.get("commodity", ""),
                        "market": cleaned.get("market", ""),

                        "min_price": float(
                            cleaned.get("min_price", 0)
                        ),

                        "max_price": float(
                            cleaned.get("max_price", 0)
                        ),

                        "modal_price": float(
                            cleaned.get("modal_price", 0)
                        ),

                        "arrivals": float(
                            cleaned.get("arrivals", 0)
                        )
                    }

                    records.append(record)

                except (ValueError, TypeError) as error:
                    print(
                        f"Skipping invalid market row: "
                        f"{cleaned} | {error}"
                    )

    except Exception as error:
        print(f"Error loading market data: {error}")
        return []

    print(f"Loaded {len(records)} market records.")

    return records


def load_demo_data():
    """
    Loads application metadata and prototype information.
    """

    if not DEMO_DATA_FILE.exists():
        return {}

    try:
        with open(DEMO_DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


# ---------------------------------------------------------
# MARKET DATA
# ---------------------------------------------------------

def get_crops():
    data = load_market_data()

    crops = sorted(
        list({
            row["commodity"]
            for row in data
            if row.get("commodity")
        })
    )

    return crops


def get_markets(commodity=None):
    data = load_market_data()

    if commodity:
        data = [
            row for row in data
            if row["commodity"].lower() == commodity.lower()
        ]

    markets = sorted(
        list({
            row["market"]
            for row in data
            if row.get("market")
        })
    )

    return markets


def get_historical_data(commodity, market):
    data = load_market_data()

    filtered = [
        row for row in data
        if row["commodity"].lower() == commodity.lower()
        and row["market"].lower() == market.lower()
    ]

    filtered.sort(key=lambda x: x["date"])

    return filtered


def get_current_market(commodity, market):
    history = get_historical_data(commodity, market)

    if not history:
        return None

    latest = history[-1]

    return {
        "date": latest["date"],
        "commodity": latest["commodity"],
        "market": latest["market"],
        "min_price": latest["min_price"],
        "max_price": latest["max_price"],
        "modal_price": latest["modal_price"],
        "arrivals": latest["arrivals"],
        "data_mode": "DEMO"
    }


# ---------------------------------------------------------
# MARKET STATISTICS
# ---------------------------------------------------------

def calculate_statistics(historical_data):

    if not historical_data:
        return {
            "average": 0,
            "highest": 0,
            "lowest": 0,
            "volatility": 0
        }

    prices = [
        row["modal_price"]
        for row in historical_data
        if row.get("modal_price") is not None
    ]

    if not prices:
        return {
            "average": 0,
            "highest": 0,
            "lowest": 0,
            "volatility": 0
        }

    average_price = mean(prices)

    if len(prices) > 1:
        volatility = pstdev(prices)
    else:
        volatility = 0

    return {
        "average": round(average_price, 2),
        "highest": round(max(prices), 2),
        "lowest": round(min(prices), 2),
        "volatility": round(volatility, 2)
    }


def calculate_trend(historical_data):

    if len(historical_data) < 2:
        return {
            "direction": "STABLE",
            "change_percent": 0
        }

    previous = historical_data[-2]["modal_price"]
    latest = historical_data[-1]["modal_price"]

    if previous == 0:
        return {
            "direction": "STABLE",
            "change_percent": 0
        }

    change_percent = ((latest - previous) / previous) * 100

    if change_percent > 2:
        direction = "RISING"
    elif change_percent < -2:
        direction = "FALLING"
    else:
        direction = "STABLE"

    return {
        "direction": direction,
        "change_percent": round(change_percent, 2)
    }


# ---------------------------------------------------------
# AI-ASSISTED OUTLOOK
# ---------------------------------------------------------

def calculate_prediction(commodity, market):

    history = get_historical_data(commodity, market)

    if len(history) < 4:
        return {
            "direction": "INSUFFICIENT DATA",
            "confidence": 0,
            "expected_range": None,
            "factors": [
                "More historical observations are required."
            ],
            "disclaimer": (
                "This AI-assisted outlook is an estimate based on "
                "available market data. It does not guarantee future "
                "prices, profits or income."
            )
        }

    prices = [
        row["modal_price"]
        for row in history
        if row.get("modal_price") is not None
    ]

    recent_window = prices[-3:]
    previous_window = prices[-6:-3] if len(prices) >= 6 else prices[:-3]

    recent_average = mean(recent_window)
    previous_average = mean(previous_window)

    if previous_average == 0:
        change = 0
    else:
        change = (
            (recent_average - previous_average)
            / previous_average
        ) * 100

    if change > 2:
        direction = "RISING"
    elif change < -2:
        direction = "FALLING"
    else:
        direction = "STABLE"

    # Prototype confidence calculation.
    # This is NOT a machine-learning confidence score.
    confidence = min(
        85,
        max(
            55,
            55 + abs(change) * 5
        )
    )

    latest_price = prices[-1]

    if direction == "RISING":
        lower = latest_price * 1.01
        upper = latest_price * 1.08

    elif direction == "FALLING":
        lower = latest_price * 0.92
        upper = latest_price * 0.99

    else:
        lower = latest_price * 0.97
        upper = latest_price * 1.03

    factors = [
        "Recent modal-price movement",
        "Short-term historical trend",
        "Observed market-price volatility",
        "Recent market observations available in the dataset"
    ]

    return {
        "direction": direction,
        "confidence": round(confidence),
        "expected_range": {
            "lower": round(lower, 2),
            "upper": round(upper, 2)
        },
        "factors": factors,
        "data_points": len(history),
        "method": "Prototype statistical trend analysis",
        "disclaimer": (
            "This AI-assisted outlook is an estimate based on "
            "available market data. It does not guarantee future "
            "prices, profits or income."
        )
    }


# ---------------------------------------------------------
# CROP ADVISORY
# ---------------------------------------------------------

ADVISORY_DATA = {

    "Tomato": {
        "crop_stage": "General crop guidance",
        "observations": [
            "Monitor crop regularly for visible pest or disease symptoms.",
            "Maintain appropriate field sanitation.",
            "Observe soil moisture before irrigation.",
            "Use locally recommended agricultural practices."
        ],
        "focus": [
            "Crop monitoring",
            "Soil moisture",
            "Field sanitation",
            "Expert consultation when symptoms appear"
        ],
        "data_mode": "PROTOTYPE"
    },

    "Onion": {
        "crop_stage": "General crop guidance",
        "observations": [
            "Regularly inspect leaves and bulbs for abnormal symptoms.",
            "Monitor field moisture conditions.",
            "Maintain appropriate field sanitation.",
            "Seek expert advice when unusual symptoms are observed."
        ],
        "focus": [
            "Crop monitoring",
            "Moisture management",
            "Field sanitation",
            "Expert consultation"
        ],
        "data_mode": "PROTOTYPE"
    }
}


def get_advisory(crop):

    if not crop:
        return {
            "crop": None,
            "observations": [],
            "focus": [],
            "data_mode": "PROTOTYPE"
        }

    if crop in ADVISORY_DATA:
        result = ADVISORY_DATA[crop].copy()
        result["crop"] = crop
        return result

    return {
        "crop": crop,
        "crop_stage": "General crop guidance",
        "observations": [
            "Monitor the crop regularly.",
            "Observe soil and weather conditions.",
            "Record unusual crop symptoms.",
            "Contact an agriculture expert for crop-specific advice."
        ],
        "focus": [
            "Crop monitoring",
            "Weather awareness",
            "Soil condition",
            "Expert consultation"
        ],
        "data_mode": "PROTOTYPE"
    }


# ---------------------------------------------------------
# AGRICULTURAL ALERTS
# ---------------------------------------------------------
# ---------------------------------------------------------
# DISEASE / PEST ALERTS
# ---------------------------------------------------------

DISEASE_ALERTS_DATA = [
    {
        "id": 1,
        "crop": "Tomato",
        "issue": "Pest/Disease Monitoring Alert",
        "location": "Pune",
        "severity": "INFO",
        "message": (
            "Regularly inspect tomato plants for unusual leaf, "
            "stem or fruit symptoms."
        ),
        "action": (
            "If symptoms are observed, capture an image and "
            "contact a qualified agriculture expert."
        ),
        "data_mode": "DEMO"
    },
    {
        "id": 2,
        "crop": "Onion",
        "issue": "Crop Health Monitoring Alert",
        "location": "Pune",
        "severity": "INFO",
        "message": (
            "Monitor onion leaves and bulbs regularly for "
            "unusual changes."
        ),
        "action": (
            "Seek expert confirmation before taking any "
            "treatment decision."
        ),
        "data_mode": "DEMO"
    }
]


def get_disease_alerts(location=None, crop=None):

    alerts = DISEASE_ALERTS_DATA

    if location:
        alerts = [
            alert for alert in alerts
            if alert["location"].lower() == location.lower()
        ]

    if crop:
        alerts = [
            alert for alert in alerts
            if alert["crop"].lower() == crop.lower()
        ]

    return alerts
ALERTS_DATA = [
    {
        "id": 1,
        "title": "Crop Monitoring Alert",
        "message": "Farmers are advised to regularly inspect crops for unusual pest or disease symptoms.",
        "severity": "INFO",
        "location": "Pune",
        "data_mode": "DEMO"
    },
    {
        "id": 2,
        "title": "Weather Awareness",
        "message": "Monitor local weather conditions before making field-management decisions.",
        "severity": "INFO",
        "location": "Pune",
        "data_mode": "DEMO"
    },
    {
        "id": 3,
        "title": "Market Observation",
        "message": "Recent commodity-price movement is available in the Market Intelligence section.",
        "severity": "INFO",
        "location": "Pune",
        "data_mode": "DEMO"
    }
]


def get_alerts(location=None):

    if not location:
        return ALERTS_DATA

    return [
        alert for alert in ALERTS_DATA
        if alert["location"].lower() == location.lower()
    ]


# ---------------------------------------------------------
# EXPERT DIRECTORY
# ---------------------------------------------------------

EXPERTS_DATA = [
    {
        "name": "Agriculture Expert",
        "specialization": "General Crop Advisory",
        "location": "Pune",
        "availability": "Demo Directory",
        "contact": "Contact details to be connected",
        "data_mode": "DEMO"
    },
    {
        "name": "Horticulture Specialist",
        "specialization": "Horticultural Crops",
        "location": "Pune",
        "availability": "Demo Directory",
        "contact": "Contact details to be connected",
        "data_mode": "DEMO"
    },
    {
        "name": "Plant Protection Expert",
        "specialization": "Pest & Disease Identification",
        "location": "Pune",
        "availability": "Demo Directory",
        "contact": "Contact details to be connected",
        "data_mode": "DEMO"
    }
]


def get_experts(location=None):

    if not location:
        return EXPERTS_DATA

    matching = [
        expert for expert in EXPERTS_DATA
        if expert["location"].lower() == location.lower()
    ]

    return matching


# ---------------------------------------------------------
# GOVERNMENT SCHEME DIRECTORY
# ---------------------------------------------------------

SCHEMES_DATA = [
    {
        "name": "PM-KISAN",
        "category": "Farmer Support",
        "description": "Government farmer-support scheme information.",
        "source_status": "Verify eligibility and current details on the official government portal.",
        "data_mode": "REFERENCE"
    },
    {
        "name": "Pradhan Mantri Fasal Bima Yojana",
        "category": "Crop Insurance",
        "description": "Crop-insurance related government scheme information.",
        "source_status": "Verify current eligibility, coverage and application details on the official government portal.",
        "data_mode": "REFERENCE"
    },
    {
        "name": "Soil Health Card",
        "category": "Soil Management",
        "description": "Government initiative providing information related to soil health and nutrient status.",
        "source_status": "Verify current services and availability through official government sources.",
        "data_mode": "REFERENCE"
    }
]


def get_schemes():

    return SCHEMES_DATA


# ---------------------------------------------------------
# AGRICULTURAL INPUT / SERVICE DIRECTORY
# ---------------------------------------------------------

INPUT_SHOPS_DATA = [
    {
        "name": "Demo Farm Supply Centre",
        "type": "Agricultural Input & Service",
        "location": "Pune",
        "distance": "Demo",
        "services": [
            "Seeds",
            "Farm supplies",
            "Agricultural guidance"
        ],
        "data_mode": "DEMO"
    },
    {
        "name": "Demo Agri Service Point",
        "type": "Farm Service Centre",
        "location": "Pune",
        "distance": "Demo",
        "services": [
            "Farm equipment information",
            "Agricultural services",
            "Expert referral"
        ],
        "data_mode": "DEMO"
    }
]


def get_input_shops(location=None):

    if not location:
        return INPUT_SHOPS_DATA

    return [
        shop for shop in INPUT_SHOPS_DATA
        if shop["location"].lower() == location.lower()
    ]


# ---------------------------------------------------------
# CROP IMAGE ANALYSIS — PROTOTYPE
# ---------------------------------------------------------

def analyze_crop_image(filename):

    """
    Prototype-only image analysis.

    No validated machine-learning model is currently connected.
    Therefore this function deliberately does NOT claim that a
    particular pest or disease has been scientifically detected.
    """

    return {
        "status": "DEMO",
        "detected": True,
        "finding": "Possible pest or crop-stress indicator",
        "confidence": 72,
        "description": (
            "This is a prototype image-analysis result. "
            "A validated crop-detection model must be connected "
            "before this feature can be used for real field diagnosis."
        ),
        "expert_required": True,
        "recommendation": (
            "Do not make treatment decisions from this result alone. "
            "Contact a qualified agriculture or plant-protection expert "
            "for confirmation."
        ),
        "filename": filename
    }
if __name__ == "__main__":
    data = load_market_data()

    print("\nMARKET DATA TEST")
    print("-" * 40)
    print("Total records:", len(data))
    print("Crops:", get_crops())
    print("Markets:", get_markets())

    print("\nTomato / Pune:")
    print(get_historical_data("Tomato", "Pune"))

    print("\nOnion / Pune:")
    print(get_historical_data("Onion", "Pune"))