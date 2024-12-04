from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/generate-payment-link', methods=['POST'])
def generate_payment_link():
    data = request.json
    payment_link = f"https://pay.example.com/{data['amount']}/{data['payment_method']}/{data['start_date']}"
    return jsonify({"status": "success", "payment_link": payment_link})

if __name__ == '__main__':
    app.run(debug=True)