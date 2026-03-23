import json
import random

# load MPs
with open("../app/data/mp.json", "r", encoding="utf-8") as f:
    mps = json.load(f)

for mp in mps:
    # realistic distribution
    attendance = random.randint(60, 98)

    questions = int(attendance * random.randint(1, 4))
    debates = int(attendance * random.uniform(0.3, 1.5))

    mp["performance"] = {
        "attendance": attendance,
        "questions": questions,
        "debates": debates
    }

# save back
with open("../app/data/mp.json", "w", encoding="utf-8") as f:
    json.dump(mps, f, indent=2)

print("✅ Realistic performance added")