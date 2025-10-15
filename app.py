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
    for s in students:
        if s["rfid_card_id"] == card_id:
            s["balance"] += amount
            break
    else:
        # Auto-register new card
        students.append({"rfid_card_id": card_id, "balance": amount})
    with open(students_file, "w") as f:
        json.dump(students, f, indent=2)
    return jsonify({"status": "ok"})

@app.route("/api/order", methods=["POST"])
def order_food():
    data = request.json
    card_id = data["rfid_card_id"]
    total = float(data["total"])
    with open(students_file) as f:
        students = json.load(f)
    for s in students:
        if s["rfid_card_id"] == card_id:
            if s["balance"] >= total:
                s["balance"] -= total
                with open(students_file, "w") as f:
                    json.dump(students, f, indent=2)
                return jsonify({"status": "ok", "new_balance": s["balance"]})
            else:
                return jsonify({"status": "error", "message": "Insufficient balance"}), 400
    return jsonify({"status": "error", "message": "Card not found"}), 404

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
