import random
import pandas as pd
import time
import os

last_decision_time = 0
DECISION_INTERVAL = 10  # seconds
load_history = []
MAX_HISTORY = 5

high_count = 0
LOW_THRESHOLD = 0.4
HIGH_THRESHOLD = 0.8
TREND_REQUIRED = 2

# Generate ONE restaurant state
def generate_restaurant_state():
    return {
        "orders_in_queue": random.randint(0, 20),
        "avg_items_per_order": round(random.uniform(1, 6), 1),

        "crew_grill": random.randint(1, 4),
        "crew_fries": random.randint(1, 3),
        "crew_assembly": random.randint(1, 4),

        "grill_busy": round(random.uniform(0.3, 1.0), 2),
        "fries_busy": round(random.uniform(0.2, 1.0), 2),
        "assembly_busy": round(random.uniform(0.3, 1.0), 2),
    }


# 🔥 Generate MANY scenarios (dataset)
data = []

for _ in range(300):  # 300 fake situations
    state = generate_restaurant_state()

    # 🎯 Create fake "load score" (target)
    load_score = (
        state["orders_in_queue"] * 0.1 +
        state["avg_items_per_order"] * 0.2 +
        state["grill_busy"] * 0.4 +
        state["assembly_busy"] * 0.3
    )

    # Keep between 0 and 1
    state["load_score"] = round(min(load_score, 1.0), 2)

    data.append(state)


# Convert to table
df = pd.DataFrame(data)

# Show first rows
#print(df.head())

print("MODEL STARTING")

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Features (inputs)
X = df.drop("load_score", axis=1)

# Target
y = df["load_score"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Test prediction
sample = X_test.iloc[[0]]
prediction = model.predict(sample)

predicted_load = prediction[0]
data_input = sample.to_dict(orient="records")[0]

print("\n==============================")
print("   🍔 SPEEDEE AI SYSTEM")
print("==============================")

# 📊 CURRENT STATE
print("\n📊 CURRENT STATE")
print(f"Orders in queue: {data_input['orders_in_queue']}")
print(f"Avg items/order: {data_input['avg_items_per_order']}")
print(f"Grill busy: {int(data_input['grill_busy'] * 100)}%")
print(f"Fries busy: {int(data_input['fries_busy'] * 100)}%")
print(f"Assembly busy: {int(data_input['assembly_busy'] * 100)}%")

# 🧠 AI ANALYSIS
print("\n🧠 AI ANALYSIS")

load = float(predicted_load)

if load >= 0.8:
    status = "🔴 HIGH"
elif load < 0.4:
    status = "🟢 LOW"
else:
    status = "🟡 MEDIUM"

print(f"Predicted load: {round(load, 2)} → {status}")

# ⚙️ RECOMMENDATIONS
print("\n⚙️ RECOMMENDATIONS")

if load >= 0.8:
    if data_input["grill_busy"] > 0.8:
        print("→ Add 1 crew to GRILL")

    if data_input["assembly_busy"] > 0.8:
        print("→ Add 1 crew to ASSEMBLY")

    if data_input["fries_busy"] < 0.4:
        print("→ Move 1 crew FROM FRIES")

elif load < 0.4:
    print("→ Consider reducing crew")

else:
    print("→ Crew is optimal")

print("\n==============================\n")

def display_dashboard(state, predicted_load):
    os.system('clear')
    print("==============================")
    print("   🍔 SPEEDEE AI SYSTEM")
    print("==============================")
    print("\n📊 CURRENT STATE")
    print(f"Orders in queue: {state['orders_in_queue']}")
    print(f"Avg items/order: {state['avg_items_per_order']}")
    print(f"Grill busy: {int(state['grill_busy'] * 100)}%")
    print(f"Fries busy: {int(state['fries_busy'] * 100)}%")
    print(f"Assembly busy: {int(state['assembly_busy'] * 100)}%")

    print("\n🧠 AI ANALYSIS")
    load = float(predicted_load)

    if load >= 0.8:
        status = "🔴 HIGH"
    elif load < 0.4:
        status = "🟢 LOW"
    else:
        status = "🟡 MEDIUM"

    print(f"Predicted load: {round(load, 2)} → {status}")

    print("\n⚙️ RECOMMENDATIONS")
    showed_any = False

    if load >= 0.8:
        if state["grill_busy"] > 0.8:
            print("→ Add 1 crew to GRILL")
            showed_any = True

        if state["assembly_busy"] > 0.8:
            print("→ Add 1 crew to ASSEMBLY")
            showed_any = True

        if state["fries_busy"] < 0.4:
            print("→ Move 1 crew FROM FRIES")
            showed_any = True

    elif load < 0.4:
        print("→ Consider reducing crew")
        showed_any = True

    else:
        print("→ Crew is optimal")
        showed_any = True

    if not showed_any:
        print("→ Monitor stations, no immediate action")

    print("\n==============================\n")

    print("🔄 Starting LIVE simulation...\n")

while True:

    state = generate_restaurant_state()

    input_df = pd.DataFrame([state])
    predicted_load = model.predict(input_df)[0]

    load_history.append(predicted_load)

    if len(load_history) > MAX_HISTORY:
        load_history.pop(0)

    smoothed_load = sum(load_history) / len(load_history)

    current_time = time.time()

    if smoothed_load >= HIGH_THRESHOLD:
        high_count += 1
    else:
        high_count = 0

    if current_time - last_decision_time >= DECISION_INTERVAL:
        if high_count >= TREND_REQUIRED:
            print("🚨 SUSTAINED HIGH LOAD → TAKE ACTION")
            display_dashboard(state, smoothed_load)
            last_decision_time = current_time
    else:
        print("⏳ Monitoring... no strong trend yet")
    
    time.sleep(3)