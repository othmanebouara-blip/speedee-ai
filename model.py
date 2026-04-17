import random
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Generate dataset
data = []

for _ in range(300):
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

    load_score = (
        state["orders_in_queue"] * 0.05 +
        state["avg_items_per_order"] * 0.1 +
        state["grill_busy"] * 0.25 +
        state["assembly_busy"] * 0.2 +
        state["fries_busy"] * 0.1
    )

    state["load_score"] = round(min(load_score, 1.0), 2)
    data.append(state)

# Train model
df = pd.DataFrame(data)

X = df.drop("load_score", axis=1)
y = df["load_score"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)

# Export model
def get_model():
    return model