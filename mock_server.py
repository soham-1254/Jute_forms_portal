from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import json

# =====================================================
# 🧠 FLASK + MONGODB SETUP
# =====================================================
app = Flask(__name__)
CORS(app)

# MongoDB connection (update only if your password or cluster changes)
MONGO_URI = "mongodb+srv://Finisher_card_sliver:Sohampanda@cluster0.mjn5qdx.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["form_to_sap"]

# =====================================================
# 🧾 JSON ENCODER FOR BSON OBJECTS
# =====================================================
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)

# =====================================================
# 🏠 ROOT ENDPOINT
# =====================================================
@app.route("/")
def home():
    return (
        "<h2>🚀 Flask + MongoDB Mock SAP OData Server</h2>"
        "<p>All Digitized Form Endpoints:</p>"
        "<ul>"
        "<li>Finisher Card Sliver → /sap/opu/odata/sap/ZFORM_API_SRV/FormEntries</li>"
        "<li>Spreader Roll Sliver → /sap/opu/odata/sap/ZSPREADER_API_SRV/FormEntries</li>"
        "<li>Inter Card Rollfeed → /sap/opu/odata/sap/ZINTERCARD_API_SRV/FormEntries</li>"
        "<li>Breaker Card Rollfeed → /sap/opu/odata/sap/ZBREAKER_API_SRV/FormEntries</li>"
        "<li>Breaker Card Handfeed → /sap/opu/odata/sap/ZHAND_API_SRV/FormEntries</li>"
        "<li>Softner Morah Weight → /sap/opu/odata/sap/ZSOFTNER_API_SRV/FormEntries</li>"
        "<li>Cleaning & Gauging → /sap/opu/odata/sap/ZCLEANING_API_SRV/FormEntries</li>"
        "<li>Maintenance Log → /sap/opu/odata/sap/ZMAINTENANCE_API_SRV/FormEntries</li>"
        "<li>Roll Stock Carding → /sap/opu/odata/sap/ZROLLSTOCK_API_SRV/FormEntries</li>"
        "<li>Roll Stock Availability → /sap/opu/odata/sap/ZROLLSTOCKAVAIL_API_SRV/FormEntries</li>"
        "<li>Batching Entry Forms → /sap/opu/odata/sap/ZBATCHING_API_SRV/FormEntries</li>"
        "<li>Raw Jute Requirement → /sap/opu/odata/sap/ZRAWJUTE_API_SRV/FormEntries</li>"
        "</ul>"
    )

# =====================================================
# 🔁 GENERIC ROUTE REGISTRATION FUNCTION
# =====================================================
def register_route(route, collection_name, label):
    """
    Dynamically register a GET + POST route for each form
    Each form stores its data in its respective MongoDB collection
    """
    collection = db[collection_name]

    def handle_request():
        if request.method == "GET":
            docs = list(collection.find({}, {"_id": 0}))
            print(f"📄 Returning {len(docs)} records from {label}.")
            return jsonify({"d": {"results": docs}}), 200

        elif request.method == "POST":
            try:
                data = request.get_json(force=True)
                result = collection.insert_one(data)
                inserted_id = str(result.inserted_id)
                data["_id"] = inserted_id
                print(f"✅ Inserted record into {label} with ID: {inserted_id}")

                return app.response_class(
                    response=json.dumps({"d": data}, cls=JSONEncoder),
                    status=201,
                    mimetype="application/json",
                )
            except Exception as e:
                print(f"❌ Error inserting record into {label}:", e)
                return jsonify({"error": str(e)}), 500

    # Each endpoint must have a unique function name (fix for AssertionError)
    endpoint_name = f"handle_request_{collection_name}"
    app.add_url_rule(
        route, endpoint=endpoint_name, view_func=handle_request, methods=["GET", "POST"]
    )

# =====================================================
# 🧱 REGISTER ALL ENDPOINTS
# =====================================================
register_route("/sap/opu/odata/sap/ZSPREADER_API_SRV/FormEntries", "Spreader_roll_sliver", "Spreader Roll Sliver")
register_route("/sap/opu/odata/sap/ZINTERCARD_API_SRV/FormEntries", "Inter_card_rollfeed", "Inter Card Rollfeed")
register_route("/sap/opu/odata/sap/ZBREAKER_API_SRV/FormEntries", "Breaker_card_rollfeed", "Breaker Card Rollfeed")
register_route("/sap/opu/odata/sap/ZHAND_API_SRV/FormEntries", "Breaker_card_handfeed", "Breaker Card Handfeed")
register_route("/sap/opu/odata/sap/ZSOFTNER_API_SRV/FormEntries", "Softner_morah_weight", "Softner Morah Weight")
register_route("/sap/opu/odata/sap/ZCLEANING_API_SRV/FormEntries", "Cleaning_gauging", "Cleaning & Gauging")
register_route("/sap/opu/odata/sap/ZMAINTENANCE_API_SRV/FormEntries", "Maintenance_log", "Maintenance Log")
register_route("/sap/opu/odata/sap/ZROLLSTOCK_API_SRV/FormEntries", "Roll_stock_carding", "Roll Stock Carding")
register_route("/sap/opu/odata/sap/ZROLLSTOCKAVAIL_API_SRV/FormEntries", "Roll_stock_availability", "Roll Stock Availability")
register_route("/sap/opu/odata/sap/ZBATCHING_API_SRV/FormEntries", "Batching_department", "Batching Entry Forms")
register_route("/sap/opu/odata/sap/ZRAWJUTE_API_SRV/FormEntries", "Raw_jute_requirement", "Raw Jute Requirement & Issue Report")
register_route("/sap/opu/odata/sap/ZRAWJUTE_ISSUE_SRV/FormEntries","Raw_jute_issue_slip","Raw Jute Issue Slip")
register_route("/sap/opu/odata/sap/ZBUNDLE_STRENGTH_SRV/FormEntries","Raw_jute_bundle_strength","Raw Jute Bundle Strength Report")
register_route("/sap/opu/odata/sap/ZCARDING_REPINNING_SRV/FormEntries","Carding_repinnning","Carding Repinning Report")
register_route("/sap/opu/odata/sap/ZDRAWING_METER_SRV/FormEntries","Drawing_meter_book","Drawing Meter Book")
register_route("/sap/opu/odata/sap/ZSTOPMOTION_API_SRV/FormEntries", "Front_back_stop_motion", "Front & Back Stop Motion")
register_route("/sap/opu/odata/sap/ZCARRIAGE_API_SRV/FormEntries","Carriage_report","Carriage Report")
register_route( "/sap/opu/odata/sap/ZREVOLVING_API_SRV/FormEntries",   "Revolving_record",   "Revolving / Slicking / Mangle Wheel / Idle Record")
register_route("/sap/opu/odata/sap/ZFINSQC_API_SRV/FormEntries","Finisher_drawing_sqc","Finisher Drawing SQC Report")
register_route("/sap/opu/odata/sap/ZWINDING_API_SRV/FormEntries","Winding_production_khata","Winding Production Khata")
register_route("/sap/opu/odata/sap/ZYARNCOUNT_API_SRV/FormEntries","Yarn_count_report","Yarn Count Report")
register_route("/sap/opu/odata/sap/ZCOPWINDING_API_SRV/FormEntries","Cop_winding_production","Cop Winding Production")
register_route("/sap/opu/odata/sap/ZSPOOLWINDING_API_SRV/FormEntries","Spool_winding_production","Spool Winding Production")
register_route("/sap/opu/odata/sap/ZMORAHWEIGHT_API_SRV/FormEntries","Morah_weight_records","Morah Weight Entry")
register_route("/sap/opu/odata/sap/ZHISTORYBOOK_API_SRV/FormEntries","History_book_records","History Book Entries")
register_route("/sap/opu/odata/sap/ZFINISHERCARD_API_SRV/FormEntries","Finisher_card_sliver","Finisher Card Sliver Weight")



# =====================================================
# 🩺 HEALTH CHECK ROUTE
# =====================================================
@app.route("/ping")
def ping():
    try:
        db.list_collection_names()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# =====================================================
# 🚀 RUN SERVER
# =====================================================
if __name__ == "__main__":
    print("🚀 Starting Flask + MongoDB Mock SAP Server on http://localhost:8080 ...")
    app.run(host="0.0.0.0", port=8080, debug=True)
