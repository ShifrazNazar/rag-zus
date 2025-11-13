"""
Script to scrape ZUS Coffee drinkware products from shop.zuscoffee.com.
Only scrapes drinkware category products.
"""
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import time

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Missing required packages. Install with:")
    print("  pip install requests beautifulsoup4")
    sys.exit(1)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Base URL for ZUS Coffee shop
BASE_URL = "https://shop.zuscoffee.com"
DRINKWARE_URL = f"{BASE_URL}/collections/drinkware"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


def clean_price(price_text: str) -> str:
    """
    Clean price text by removing prefixes like "Sale price", "Price", etc.
    Handles both spaced and concatenated versions (e.g., "Sale priceRM79.00").
    
    Args:
        price_text: Raw price text
        
    Returns:
        Cleaned price text (e.g., "RM79.00") or None
    """
    if not price_text:
        return None
    
    # Remove common prefixes (case insensitive)
    prefixes = [
        "sale price",
        "price",
        "regular price",
        "original price",
        "now",
        "from"
    ]
    
    cleaned = price_text.strip()
    for prefix in prefixes:
        # Remove prefix if it appears at the start (case insensitive)
        # Handle both spaced and concatenated versions
        prefix_lower = prefix.lower()
        cleaned_lower = cleaned.lower()
        
        if cleaned_lower.startswith(prefix_lower):
            # Remove the prefix
            cleaned = cleaned[len(prefix):].strip()
            break  # Only remove the first matching prefix
    
    # Clean up any extra whitespace
    cleaned = ' '.join(cleaned.split())
    
    return cleaned if cleaned else None


def scrape_product_page(product_url: str) -> Dict[str, Any]:
    """
    Scrape individual product page for detailed description.
    
    Args:
        product_url: Full URL to product page
        
    Returns:
        Dictionary with product details (mainly description)
    """
    try:
        response = requests.get(product_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product name
        name_elem = soup.find('h1') or soup.find('h2', class_=lambda x: x and 'product' in str(x).lower() and 'title' in str(x).lower())
        name = name_elem.get_text(strip=True) if name_elem else None
        
        # Extract description - try multiple methods
        description = None
        
        # Method 1: Look for product description sections
        desc_selectors = [
            'div[class*="product-description"]',
            'div[class*="product__description"]',
            'div[id*="product-description"]',
            'div[class*="description"]',
            '.product-details',
            '.product-info'
        ]
        
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                description = desc_elem.get_text(strip=True)
                break
        
        # Method 2: Look for meta description
        if not description:
            meta_desc = soup.find('meta', {'property': 'og:description'})
            if meta_desc:
                description = meta_desc.get('content', '')
        
        # Method 3: Look for any paragraph in product sections
        if not description:
            product_sections = soup.find_all(['div', 'section'], class_=lambda x: x and 'product' in str(x).lower())
            for section in product_sections:
                paragraphs = section.find_all('p')
                if paragraphs:
                    description = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])  # First 3 paragraphs
                    break
        
        # Extract price
        price_elem = soup.find('sale-price') or \
                    soup.find('span', class_=lambda x: x and 'price' in str(x).lower()) or \
                    soup.find('div', class_=lambda x: x and 'price' in str(x).lower())
        price = None
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price = clean_price(price_text)
        
        # Clean up description
        if description:
            description = ' '.join(description.split())
            if len(description) > 500:
                description = description[:500] + "..."
        else:
            description = "Premium drinkware product from ZUS Coffee."
        
        return {
            "name": name,
            "description": description,
            "price": price
        }
        
    except Exception as e:
        logger.warning(f"Error scraping product page {product_url}: {e}")
        return {}


def extract_product_from_card(card_elem) -> Dict[str, Any]:
    """
    Extract product information from a product card element.
    
    Args:
        card_elem: BeautifulSoup element containing product card
        
    Returns:
        Dictionary with product details or None
    """
    try:
        # Find product link
        link_elem = card_elem.find('a', href=lambda x: x and '/products/' in x)
        if not link_elem:
            return None
        
        href = link_elem.get('href', '')
        if href.startswith('/'):
            product_url = BASE_URL + href
        elif href.startswith('http'):
            product_url = href
        else:
            product_url = BASE_URL + '/' + href
        
        # Remove query parameters
        product_url = product_url.split('?')[0].split('#')[0]
        
        # Extract product name from product-card__title
        title_elem = card_elem.find('span', class_='product-card__title')
        if title_elem:
            name_link = title_elem.find('a')
            name = name_link.get_text(strip=True) if name_link else title_elem.get_text(strip=True)
        else:
            # Fallback: try to find any heading or title
            name_elem = card_elem.find(['h2', 'h3', 'h4']) or card_elem.find('span', class_=lambda x: x and 'title' in str(x).lower())
            name = name_elem.get_text(strip=True) if name_elem else "Unknown Product"
        
        # Extract category from product-card__category
        category_elem = card_elem.find('span', class_='product-card__category')
        category = category_elem.get_text(strip=True) if category_elem else None
        
        # Extract price from sale-price
        price_elem = card_elem.find('sale-price') or card_elem.find('span', class_=lambda x: x and 'price' in str(x).lower())
        price = None
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price = clean_price(price_text)
        
        # Build description from available info
        description = f"Premium {category.lower() if category else 'drinkware'} product from ZUS Coffee."
        if name:
            description = f"{name}. {description}"
        
        return {
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "url": product_url
        }
        
    except Exception as e:
        logger.warning(f"Error extracting product from card: {e}")
        return None


def scrape_drinkware_products() -> List[Dict[str, Any]]:
    """
    Scrape all drinkware products from ZUS Coffee shop.
    Extracts products from listing page cards, then optionally scrapes individual pages for descriptions.
    
    Returns:
        List of product dictionaries
    """
    products = []
    
    try:
        logger.info(f"Fetching drinkware page: {DRINKWARE_URL}")
        response = requests.get(DRINKWARE_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all product cards using the actual structure
        product_cards = []
        
        # Try to find product-card__info elements
        cards = soup.find_all('div', class_=lambda x: x and 'product-card__info' in str(x))
        if cards:
            product_cards = cards
            logger.info(f"Found {len(cards)} product cards using product-card__info")
        else:
            # Fallback: look for product-card elements
            cards = soup.find_all('div', class_=lambda x: x and 'product-card' in str(x))
            if cards:
                product_cards = cards
                logger.info(f"Found {len(cards)} product cards using product-card")
            else:
                # Last resort: find any div containing product links
                all_divs = soup.find_all('div')
                for div in all_divs:
                    if div.find('a', href=lambda x: x and '/products/' in x):
                        product_cards.append(div)
                logger.info(f"Found {len(product_cards)} product cards using fallback method")
        
        # Extract products from cards
        seen_urls = set()
        for card in product_cards:
            product = extract_product_from_card(card)
            if product and product['url'] not in seen_urls:
                seen_urls.add(product['url'])
                products.append(product)
                logger.debug(f"Extracted: {product['name']}")
        
        logger.info(f"Extracted {len(products)} products from listing page")
        
        # Optionally scrape individual product pages for better descriptions
        # This is optional and can be disabled to speed up scraping
        scrape_individual_pages = True
        if scrape_individual_pages and products:
            logger.info("Scraping individual product pages for detailed descriptions...")
            for i, product in enumerate(products, 1):
                try:
                    logger.info(f"Fetching details for product {i}/{len(products)}: {product['name']}")
                    detailed_product = scrape_product_page(product['url'])
                    if detailed_product:
                        # Update with detailed info, keep original if detailed scrape fails
                        product['description'] = detailed_product.get('description', product.get('description', ''))
                        if detailed_product.get('price') and not product.get('price'):
                            product['price'] = detailed_product['price']
                    time.sleep(1)  # Be respectful with requests
                except Exception as e:
                    logger.warning(f"Error fetching details for {product['url']}: {e}")
                    continue
        
        # Add IDs
        for i, product in enumerate(products, 1):
            product['id'] = i
            
    except requests.RequestException as e:
        logger.error(f"Error fetching drinkware page: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise
    
    if not products:
        logger.warning("No products found.")
        return []
    
    return products


def main():
    """Main function to scrape and save products."""
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / "data" / "products"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting product scraping...")
    products = scrape_drinkware_products()
    
    if not products:
        logger.error("No products scraped. Exiting.")
        sys.exit(1)
    
    # Save to JSON
    output_file = data_dir / "products.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Saved {len(products)} products to {output_file}")
    logger.info("Product scraping complete!")


if __name__ == "__main__":
    main()

