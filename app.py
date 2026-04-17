from flask import Flask, jsonify
import random
from model import get_model

model = get_model()

app = Flask(__name__)

import pandas as pd
import random

def generate_real_data():
    state = {
    "orders_in_queue": random.randint(0, 20),
    "avg_items_per_order": round(random.uniform(1, 6), 1),

    "crew_grill": random.randint(1, 4),
    "crew_fries": random.randint(1, 3),
    "crew_assembly": random.randint(1, 4),

    "grill_busy": round(random.uniform(0.3, 1.0), 2),
    "fries_busy": round(random.uniform(0.2, 1.0), 2),
    "assembly_busy": round(random.uniform(0.3, 1.0), 2),
}

    input_df = pd.DataFrame([state])
    predicted_load = model.predict(input_df)[0]

    # Simple recommendation logic

    recommendations = []

    if predicted_load >= 0.8:
        if state["grill_busy"] > 0.75:
         recommendations.append("🔥 Add crew to GRILL")

        if state["assembly_busy"] > 0.75:
         recommendations.append("📦 Add crew to ASSEMBLY")

        if state["fries_busy"] < 0.5:
         recommendations.append("🍟 Move crew FROM FRIES")

        if not recommendations:
         recommendations.append("⚠️ High load - monitor closely")

    elif predicted_load < 0.4:
        recommendations.append("🟢 Reduce crew / slow period")

    else:
        recommendations.append("🟡 System stable")

    return {
        **state,
        "predicted_load": round(predicted_load, 2),
        "recommendations": recommendations
    }

@app.route("/data")
def data():
    return jsonify(generate_real_data())

@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Speedee AI Dashboard</title>
        <script>
        let highLoadCount = 0;
            async function fetchData() {
                const res = await fetch('/data');
                const data = await res.json();

                document.getElementById("orders").innerText = data.orders_in_queue || data.orders;
                const loadElement = document.getElementById("load");
                const load = data.predicted_load;
                const alertElement = document.getElementById("alert");

                const statusElement = document.getElementById("status");

                loadElement.innerText = load.toFixed(2);

                // Color logic
                if (load >= 0.8) {
                    highLoadCount++;

                    loadElement.style.color = "red";
                    statusElement.innerText = "HIGH";

                    if (highLoadCount >= 3) {
                        alertElement.innerText = "🚨 HIGH LOAD - TAKE ACTION";
                    } else {
                        alertElement.innerText = "⚠️ Rising load...";
                    }

                } else if (load < 0.4) {
                    highLoadCount = 0;

                    loadElement.style.color = "green";
                    statusElement.innerText = "LOW";
                    alertElement.innerText = "";

                } else {
                    highLoadCount = 0;

                    loadElement.style.color = "orange";
                    statusElement.innerText = "MEDIUM";
                    alertElement.innerText = "";
                }
                document.getElementById("grill").innerText = data.grill_busy;
                document.getElementById("fries").innerText = data.fries_busy;
                document.getElementById("assembly").innerText = data.assembly_busy;
                const recList = document.getElementById("recommendations");
                recList.innerHTML = "";

                if (data.recommendations.length === 0) {
                    recList.innerHTML = "<li>No action needed</li>";
                } else {
                   data.recommendations.forEach(rec => {
                     const li = document.createElement("li");
                     li.innerText = "→ " + rec;
                     recList.appendChild(li);
        
                 });
            }  
            }

            setInterval(fetchData, 2000);
        </script>
    </head>

    <body style="font-family: Arial; text-align: center;">
        <h1>🍔 SPEEDEE AI DASHBOARD</h1>

        <h2>Orders: <span id="orders">0</span></h2>
        <h2>
          Predicted Load: <span id="load">0</span>
          (<span id="status">-</span>)
        </h2>
        <h3>Grill: <span id="grill"></span></h3>
        <h3>Fries: <span id="fries"></span></h3>
        <h3>Assembly: <span id="assembly"></span></h3>

        <h2>Recommendations</h2>
        <ul id="recommendations" style="list-style: none; padding: 0;"></ul>
        <h2 id="alert" style="color:red;"></h2>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)