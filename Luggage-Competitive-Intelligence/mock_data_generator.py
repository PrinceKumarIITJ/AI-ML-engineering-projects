import pandas as pd
import numpy as np
import random
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

BRANDS = ['Safari', 'Skybags', 'VIP', 'American Tourister']

# Base templates for product generation
PRODUCT_ADJECTIVES = ['Premium', 'Lightweight', 'Durable', 'Hard Sided', 'Soft Sided', 'Expandable', 'Cabin', 'Check-in', 'Stylish', 'Polycarbonate']
NOUNS = ['Trolley Bag', 'Suitcase', 'Luggage', 'Spinner', 'Duffle Bag']

def generate_products():
    products = []
    pid_counter = 1
    
    # Brand positioning
    brand_configs = {
        'Safari': {'mrp_range': (3000, 6000), 'discount_range': (0.4, 0.7), 'rating_mu': 4.1, 'rating_sigma': 0.3},
        'Skybags': {'mrp_range': (4000, 7000), 'discount_range': (0.3, 0.6), 'rating_mu': 4.0, 'rating_sigma': 0.4},
        'VIP': {'mrp_range': (5000, 10000), 'discount_range': (0.2, 0.5), 'rating_mu': 4.3, 'rating_sigma': 0.3},
        'American Tourister': {'mrp_range': (6000, 12000), 'discount_range': (0.1, 0.4), 'rating_mu': 4.4, 'rating_sigma': 0.2}
    }
    
    for brand in BRANDS:
        # Generate 15 products per brand
        for _ in range(15):
            title = f"{brand} {random.choice(PRODUCT_ADJECTIVES)} {random.choice(NOUNS)} {random.choice([55, 65, 75])}cm"
            config = brand_configs[brand]
            
            mrp = random.randint(config['mrp_range'][0], config['mrp_range'][1])
            discount = random.uniform(config['discount_range'][0], config['discount_range'][1])
            price = int(mrp * (1 - discount))
            # Round to nearest 99
            price = (price // 100) * 100 + 99
            discount_pct = round(((mrp - price) / mrp) * 100, 2)
            
            rating = round(np.random.normal(config['rating_mu'], config['rating_sigma']), 1)
            rating = min(max(rating, 1.0), 5.0)
            
            num_reviews = int(np.random.lognormal(mean=6, sigma=1)) + 10
            
            products.append({
                'Product_ID': f'P{pid_counter:04d}',
                'Brand': brand,
                'Title': title,
                'Category': 'Luggage & Travel Gear',
                'Price': price,
                'MRP': mrp,
                'Discount_Pct': discount_pct,
                'Rating': rating,
                'Num_Reviews': num_reviews,
                'URL': f"https://amazon.in/dp/mock{pid_counter}"
            })
            pid_counter += 1
            
    return pd.DataFrame(products)

def generate_reviews(products_df):
    reviews = []
    rid_counter = 1
    
    # Review components
    positive_aspects = {
        'wheels': ['smooth wheels', 'wheels glide easily', '360 degree wheels are great', 'roller is excellent'],
        'handle': ['sturdy handle', 'telescopic handle is good', 'handle feels strong', 'comfortable grip'],
        'material': ['tough material', 'looks premium', 'scratch resistant', 'hard shell is good'],
        'zipper': ['smooth zipper', 'heavy duty zips', 'zipper works fine', 'secure lock and zips'],
        'size': ['spacious', 'perfect cabin size', 'fits a lot', 'good capacity'],
        'durability': ['very durable', 'survived flight drops', 'long lasting', 'sturdy build']
    }
    
    negative_aspects = {
        'wheels': ['wheels got stuck', 'broken wheel after 1 trip', 'wheels are noisy', 'won\'t roll straight'],
        'handle': ['handle jammed', 'flimsy handle', 'wobbly handle', 'handle broke'],
        'material': ['scratches easily', 'cheap plastic', 'dent on arrival', 'material feels thin'],
        'zipper': ['zipper broke instantly', 'teeth misaligned', 'stuck zipper', 'poor quality zips'],
        'size': ['smaller than expected', 'doesn\'t fit 15kg', 'too bulky', 'awkward dimensions'],
        'durability': ['broke on first use', 'cracked shell', 'not durable at all', 'poor quality over time']
    }
    
    # Generate ~60 reviews per brand distributed across its products
    for brand in BRANDS:
        brand_products = products_df[products_df['Brand'] == brand]['Product_ID'].tolist()
        
        # Determine anomaly/trust signal traits for the brand to ensure the dashboard has interesting insights
        # E.g. Skybags -> high rating but durability complaints (anomaly)
        # Safari -> suspicious repetition (trust signal)
        
        for _ in range(65):
            prod_id = random.choice(brand_products)
            prod_rating = products_df[products_df['Product_ID'] == prod_id]['Rating'].values[0]
            
            # Review rating somewhat correlated to product rating
            rev_rating_raw = np.random.normal(prod_rating, 1.0)
            
            # Inject Anomalies based on brand
            is_suspicious = False
            
            if brand == 'Skybags' and random.random() < 0.3:
                # Anomaly: 4/5 star rating but negative durability review
                rev_rating = random.choice([4, 5])
                text = f"The bag looks good and the size is great. But {random.choice(negative_aspects['durability'])}. Surprising for this rating."
                
            elif brand == 'Safari' and random.random() < 0.2:
                # Trust Issue: Suspicious repetition
                rev_rating = 5
                text = "Excellent product very good quality I love this bag very much value for money."
                is_suspicious = True
                
            elif brand == 'VIP' and random.random() < 0.2:
                 # High value, positive reviews
                 rev_rating = random.choice([4, 5])
                 text = f"Worth the price. {random.choice(positive_aspects['material'])} and {random.choice(positive_aspects['wheels'])}."
                 
            else:
                rev_rating = int(min(max(rev_rating_raw, 1), 5))
                # Generate generic review text based on rating
                if rev_rating >= 4:
                    aspect1 = random.choice(list(positive_aspects.keys()))
                    aspect2 = random.choice([k for k in positive_aspects.keys() if k != aspect1])
                    text = f"Good product. {random.choice(positive_aspects[aspect1])}. Also {random.choice(positive_aspects[aspect2])}."
                elif rev_rating == 3:
                    text = f"Average bag. {random.choice(positive_aspects['size'])}, but {random.choice(negative_aspects['handle'])}."
                else:
                    aspect1 = random.choice(list(negative_aspects.keys()))
                    text = f"Disappointed. {random.choice(negative_aspects[aspect1])}. Would not recommend."

            # Date generation
            if is_suspicious:
                 # Cluster suspicious reviews around a specific date
                 date = f"2023-10-{random.randint(10, 15)}"
            else:
                 month = random.randint(1, 12)
                 day = random.randint(1, 28)
                 date = f"2023-{month:02d}-{day:02d}"

            reviews.append({
                'Review_ID': f'R{rid_counter:05d}',
                'Product_ID': prod_id,
                'Brand': brand,
                'Rating': rev_rating,
                'Review_Text': text,
                'Date': date,
                'Verified_Purchase': random.choice([True, True, True, False]) # 75% verified
            })
            rid_counter += 1
            
    return pd.DataFrame(reviews)

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    
    print("Generating mock products...")
    df_products = generate_products()
    df_products.to_csv('data/raw_products.csv', index=False)
    
    print("Generating mock reviews...")
    df_reviews = generate_reviews(df_products)
    df_reviews.to_csv('data/raw_reviews.csv', index=False)
    
    print(f"Generated {len(df_products)} products and {len(df_reviews)} reviews.")
    print("Data saved to /data directory.")
