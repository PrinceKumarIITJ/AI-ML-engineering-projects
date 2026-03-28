from fastapi import FastAPI, HTTPException
import pandas as pd

# Load cleaned data
df = pd.read_csv("data/startups_clean.csv")

# Initialize the app
app = FastAPI(title="Startup Profiler API")

# ------------------- Routes -------------------

@app.get("/")
def home():
    return {"message": "Welcome to the Startup Profiler API "}

@app.get("/summary")
def summary():
    return {
        "total_companies": len(df),
        "average_revenue": round(df["Revenue"].mean(), 2),
        "average_growth_percent": round(df["Growth %"].mean(), 2)
    }

@app.get("/industry-distribution")
def industry_distribution():
    return df["Industry"].value_counts().to_dict()

@app.get("/company/{name}")
def company_details(name: str):
    company = df[df["Company Name"].str.lower() == name.lower()]
    if company.empty:
        raise HTTPException(status_code=404, detail="Company not found")
    return company.to_dict(orient="records")[0]

@app.get("/top-growth")
def top_growth_companies():
    top = df.sort_values(by="Growth %", ascending=False).head(5)
    return top.to_dict(orient="records")
