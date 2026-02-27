# /// script
# requires-python = ">=3.11"
# dependencies = ["openai", "pandas"]
# ///

import pandas as pd
import os
from openai import OpenAI
from collections import Counter

df = pd.read_csv("news_headlines.csv")
headlines = df["headline"].tolist()
print(f"Loaded {len(headlines)} headlines")

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)

VALID = {"Politics", "Sports", "Technology", "Business", "Entertainment"}

# Use the EXACT prompt from the problem statement
def classify(headline):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{
            "role": "user",
            "content": (
                "Classify this news headline into exactly one of: "
                "Politics, Sports, Technology, Business, Entertainment.\n"
                "Reply with ONLY the category name, nothing else.\n\n"
                f"Headline: {headline}"
            )
        }]
    )
    label = resp.choices[0].message.content.strip()
    return label if label in VALID else "Business"

topics = []
for i, h in enumerate(headlines):
    label = classify(h)
    topics.append(label)
    if (i + 1) % 20 == 0:
        print(f"  {i+1}/200")

df["topic"] = topics
df.to_csv("results.csv", index=False)

counts = Counter(topics)
print("\nAll counts:", dict(counts))
print(f"\nTechnology count: {counts['Technology']}")
print("\nTechnology headlines:")
for h, t in zip(headlines, topics):
    if t == "Technology":
        print(f"  {h}")
