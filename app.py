import threading
import serial
import time
from flask import Flask, jsonify, render_template, request
import json

app = Flask(__name__)

SERIAL_PORT = "COM4"   # change if needed
BAUD_RATE = 115200

LATEST_CARD_ID = None
students_file = "students.json"
menu_file = "menu.json"

# -------------------- Serial Thread --------------------

def serial_listener():
    global LATEST_CARD_ID
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[Serial] Listening on {SERIAL_PORT}...")
        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if line.startswith("CARD:"):
                uid = line[5:].strip().upper()
                LATEST_CARD_ID = uid
                print(f"[Serial] Card detected: {uid}")
            time.sleep(0.1)
    except Exception as e:
        print("[Serial Error]:", e)

# start serial listener thread
threading.Thread(target=serial_listener, daemon=True).start()

# -------------------- Routes --------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/latest-card")
def get_latest_card():
    global LATEST_CARD_ID
    return jsonify({"rfid_card_id": LATEST_CARD_ID})

@app.route("/api/students")
def get_students():
    with open(students_file) as f:
        return jsonify(json.load(f))

@app.route("/api/menu")
def get_menu():
    with open(menu_file) as f:
        return jsonify(json.load(f))

@app.route("/api/add-balance", methods=["POST"])
def add_balance():
    data = request.json
    card_id = data["rfid_card_id"]
    amount = float(data["amount"])
    
    with open(students_file) as f:
        students = json.load(f)

    student = next((s for s in students if s["rfid_card_id"] == card_id), None)

    if student:
        student["balance"] += amount
    else:
        # Auto-register new card
        student = {"rfid_card_id": card_id, "balance": amount}
        students.append(student)

    with open(students_file, "w") as f:
        json.dump(students, f, indent=2)

    return jsonify({
        "status": "ok",
        "newBalance": student["balance"]
    })


@app.route("/api/order", methods=["POST"])
def order_food():
    data = request.get_json()
    card_id = data.get("rfid_card_id")
    items = data.get("items", [])

    if not card_id or not items:
        return jsonify({"error": "Invalid order data"}), 400

    # Load student and menu
    with open("students.json", "r") as f:
        students = json.load(f)
    with open("menu.json", "r") as f:
        menu = json.load(f)

    student = next((s for s in students if s["rfid_card_id"] == card_id), None)
    if not student:
        return jsonify({"error": "Card not found"}), 404

    # Calculate total from items
    total = 0
    for item in items:
        food = item["food"]
        qty = item["qty"]
        price = next((m["price"] for m in menu if m["food"] == food), 0)
        total += price * qty

    if student["balance"] < total:
        return jsonify({"error": "Insufficient balance"}), 400

    student["balance"] -= total

    with open("students.json", "w") as f:
        json.dump(students, f, indent=2)

    return jsonify({"total": total, "newBalance": student["balance"]})


# -------------------- Debug helper --------------------

# def debug_loop():
#     global LATEST_CARD_ID
#     while True:
#         time.sleep(2)
#         print("[Debug] LATEST_CARD_ID =", LATEST_CARD_ID)

# threading.Thread(target=debug_loop, daemon=True).start()

# -------------------- Main --------------------

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
