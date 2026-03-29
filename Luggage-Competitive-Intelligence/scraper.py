import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import random
import os

BRANDS = ['Safari', 'Skybags', 'VIP', 'American Tourister']
BASE_URL = "https://www.amazon.in/s?k="

products_data = []
reviews_data = []

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

async def stealth_scrape(page, url):
    await page.set_extra_http_headers({
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
    })
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    # Simulate human behavior
    await page.mouse.wheel(0, 500)
    await asyncio.sleep(random.uniform(2, 5))
    return await page.content()

async def scrape_brand_products(browser, brand):
    print(f"Scraping products for {brand}...")
    context = await browser.new_context(user_agent=random.choice(user_agents))
    page = await context.new_page()
    
    url = f"{BASE_URL}{brand}+luggage"
    try:
        html = await stealth_scrape(page, url)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find product blocks
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        count = 0
        
        for item in items:
            if count >= 15: # Gather ~15 items per brand
                break
                
            asin = item.get('data-asin')
            title_elem = item.find('span', {'class': 'a-size-base-plus a-color-base a-text-normal'})
            if not title_elem:
                title_elem = item.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
            
            title = title_elem.text.strip() if title_elem else ""
            
            # Ensure it's for the right brand (mostly)
            if brand.lower() not in title.lower():
                continue
                
            price_elem = item.find('span', {'class': 'a-price-whole'})
            mrp_elem = item.find('span', {'class': 'a-text-price'})
            
            price = float(price_elem.text.replace(',', '')) if price_elem else None
            mrp = float(mrp_elem.find('span', {'aria-hidden': 'true'}).text.replace('₹', '').replace(',', '')) if mrp_elem else price
            
            rating_elem = item.find('i', {'class': 'a-icon-star-small'})
            rating = float(rating_elem.text.split(' ')[0]) if rating_elem else None
            
            reviews_count_elem = item.find('span', {'class': 'a-size-base s-underline-text'})
            reviews_count = int(reviews_count_elem.text.replace(',', '')) if reviews_count_elem else 0
            
            product_url = "https://amazon.in" + item.find('a', {'class': 'a-link-normal s-no-outline'})['href'] if item.find('a', {'class': 'a-link-normal s-no-outline'}) else None
            
            if title and price:
                products_data.append({
                    'ASIN': asin,
                    'Brand': brand,
                    'Title': title,
                    'Category': 'Luggage',
                    'Price': price,
                    'MRP': mrp,
                    'Rating': rating,
                    'Num_Reviews': reviews_count,
                    'URL': product_url
                })
                count += 1
                print(f"Found: {title[:30]}... | M:{mrp} | P:{price}")
                
                # Fetch reviews for this product
                if product_url:
                    await scrape_product_reviews(context, product_url, asin, brand)
                    
    except Exception as e:
        print(f"Error scraping {brand}: {e}")
    finally:
        await context.close()

async def scrape_product_reviews(context, product_url, asin, brand):
    # Navigate to review page
    # Amazon review URL structure: /product-reviews/[ASIN]/
    review_url = f"https://www.amazon.in/product-reviews/{asin}/"
    page = await context.new_page()
    try:
        html = await stealth_scrape(page, review_url)
        soup = BeautifulSoup(html, 'html.parser')
        
        review_blocks = soup.find_all('div', {'data-hook': 'review'})
        review_count = 0
        
        for rev in review_blocks:
            if review_count >= 5: # Fetch 5 reviews per product to reach 50+ per brand
                break
                
            rev_id = rev.get('id')
            rev_rating_elem = rev.find('i', {'data-hook': 'review-star-rating'})
            rev_rating = float(rev_rating_elem.text.split(' ')[0]) if rev_rating_elem else None
            
            rev_text_elem = rev.find('span', {'data-hook': 'review-body'})
            rev_text = rev_text_elem.text.strip() if rev_text_elem else ""
            
            rev_date_elem = rev.find('span', {'data-hook': 'review-date'})
            rev_date = rev_date_elem.text.strip() if rev_date_elem else ""
            
            if rev_rating and rev_text:
                reviews_data.append({
                    'Review_ID': rev_id,
                    'Product_ID': asin,
                    'Brand': brand,
                    'Rating': rev_rating,
                    'Review_Text': rev_text.replace('\n', ' '),
                    'Date': rev_date
                })
                review_count += 1
                
    except Exception as e:
        print(f"Error scraping reviews for {asin}: {e}")
    finally:
        await page.close()

async def main():
    print("WARNING: Scraping Amazon relies on specific DOM structures and avoids bot protection.")
    print("If this fails (CAPTCHAs), use `mock_data_generator.py` instead for downstream tasks.")
    
    os.makedirs('data', exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for brand in BRANDS:
            await scrape_brand_products(browser, brand)
            # Add delay to prevent IP ban
            await asyncio.sleep(random.uniform(5, 10))
            
        await browser.close()
        
    df_prods = pd.DataFrame(products_data)
    df_revs = pd.DataFrame(reviews_data)
    
    df_prods.to_csv('data/raw_products.csv', index=False)
    df_revs.to_csv('data/raw_reviews.csv', index=False)
    print(f"Successfully scraped {len(products_data)} products and {len(reviews_data)} reviews.")

if __name__ == "__main__":
    asyncio.run(main())
