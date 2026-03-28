# ---------------- Stage 1: Data Cleaning ----------------

import pandas as pd

# Read raw scraped data
df = pd.read_csv("data/startups_raw.csv")

# Drop missing and duplicate entries
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

# Convert revenue values like "$12M", "$450K", etc.
def convert_revenue(value):
    try:
        value = value.replace('$', '').replace(',', '').strip()
        if 'M' in value:
            return float(value.replace('M', '')) * 1_000_000
        elif 'K' in value:
            return float(value.replace('K', '')) * 1_000
        else:
            return float(value)
    except:
        return None

# Convert growth percent like "45%" to float
def convert_growth(value):
    try:
        return float(value.replace('%', '').strip())
    except:
        return None

# Apply conversion functions
df['Revenue'] = df['Revenue'].apply(convert_revenue)
df['Growth %'] = df['Growth %'].apply(convert_growth)

# Drop rows with invalid values after conversion
df.dropna(subset=['Revenue', 'Growth %'], inplace=True)

# Save cleaned dataset
df.to_csv("data/startups_clean.csv", index=False)
print("✅ Cleaned data saved to 'data/startups_clean.csv'")


# ---------------- Stage 2: Visualization & Summary ----------------

import matplotlib.pyplot as plt
import seaborn as sns

# Read cleaned data
df = pd.read_csv("data/startups_clean.csv")

# ------- Plot 1: Top 5 industries by number of companies -------
industry_top5 = df['Industry'].value_counts().head(5)

plt.figure(figsize=(8, 5))
sns.barplot(x=industry_top5.values, y=industry_top5.index, palette="viridis")
plt.title("Top 5 Industries by Company Count")
plt.xlabel("Number of Companies")
plt.ylabel("Industry")
plt.tight_layout()
plt.savefig("visuals/top_5_industries.png")
plt.close()

# ------- Plot 2: Revenue Distribution -------
plt.figure(figsize=(8, 5))
sns.histplot(df['Revenue'], bins=10, kde=True, color='skyblue')
plt.title("Revenue Distribution")
plt.xlabel("Revenue ($)")
plt.ylabel("Number of Companies")
plt.tight_layout()
plt.savefig("visuals/revenue_distribution.png")
plt.close()

# ------- Plot 3: Growth % Distribution -------
plt.figure(figsize=(8, 5))
sns.histplot(df['Growth %'], bins=10, kde=True, color='salmon')
plt.title("Growth % Distribution")
plt.xlabel("Growth (%)")
plt.ylabel("Number of Companies")
plt.tight_layout()
plt.savefig("visuals/growth_distribution.png")
plt.close()

# ------- Summary Stats -------
summary = {
    "Total Companies": len(df),
    "Average Revenue": round(df['Revenue'].mean(), 2),
    "Median Revenue": round(df['Revenue'].median(), 2),
    "Average Growth (%)": round(df['Growth %'].mean(), 2),
    "Median Growth (%)": round(df['Growth %'].median(), 2)
}

print("\n📊 Summary:")
for k, v in summary.items():
    print(f"{k}: {v}")

# Save summary to file
with open("visuals/summary.txt", "w") as file:
    for k, v in summary.items():
        file.write(f"{k}: {v}\n")

print("\n✅ Summary and plots saved to 'visuals/' folder.")
