import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd

# URL of the Growjo homepage
url = "https://growjo.com/"

# Create a scraper that bypasses Cloudflare
scraper = cloudscraper.create_scraper()
response = scraper.get(url)
print("Status Code:", response.status_code)

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find the main table containing company data
table = soup.find("table", class_="jss31")
rows = table.find_all("tr")

data = []
for row in rows[1:]:
    cols = row.find_all("td")
    if len(cols) >= 9:
        company = cols[1].text.strip()
        country = cols[3].text.strip()
        industry = cols[5].text.strip()
        revenue = cols[7].text.strip()
        growth = cols[8].text.strip()

        data.append([company, industry, country, revenue, growth])

# Create DataFrame and save to CSV
df = pd.DataFrame(data, columns=["Company Name", "Industry", "Country", "Revenue", "Growth %"])
print(df.head())

df.to_csv("data/startups_raw.csv", index=False)
print("Data saved to data/startups_raw.csv ✅")
