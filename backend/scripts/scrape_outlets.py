"""
Script to scrape ZUS Coffee outlets from zuscoffee.com.
Scrapes outlets page by page from KL/Selangor region.
Source: https://zuscoffee.com/category/store/kuala-lumpur-selangor/
"""
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
import time
import re
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Missing required packages. Install with:")
    print("  pip install requests beautifulsoup4")
    sys.exit(1)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import SessionLocal, Outlet, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Base URL for ZUS Coffee outlets
BASE_URL = "https://zuscoffee.com"
OUTLETS_BASE_URL = f"{BASE_URL}/category/store/"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Maximum pages to scrape (safety limit - website shows up to Page 22)
MAX_PAGES_PER_REGION = 25


def find_pagination_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """
    Find pagination links on the current page.
    Looks for links with class "page-numbers" containing /page/2/, /page/3/, etc.
    Also extracts the last page number to build complete pagination list.
    
    Args:
        soup: BeautifulSoup object of the page
        base_url: Base URL for resolving relative links
        
    Returns:
        List of pagination URLs
    """
    pagination_urls = []
    max_page_num = 0
    
    # Find all links with class "page-numbers"
    page_links = soup.find_all('a', class_=lambda x: x and 'page-numbers' in x)
    
    for link in page_links:
        href = link.get('href', '')
        text = link.get_text(strip=True).lower()
        
        # Skip "Previous" text links
        if text == 'previous':
            continue
        
        # Check if it's a pagination link with /page/ in URL
        if '/page/' in href.lower():
            # Extract page number
            page_match = re.search(r'/page/(\d+)', href, re.I)
            if page_match:
                page_num = int(page_match.group(1))
                max_page_num = max(max_page_num, page_num)
            
            # Resolve relative URLs
            if href.startswith('/'):
                full_url = BASE_URL + href
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = urljoin(base_url, href)
            
            # Only include if it's a different page and for KL/Selangor
            if full_url not in pagination_urls and full_url != base_url:
                if 'kuala-lumpur-selangor' in full_url.lower():
                    pagination_urls.append(full_url)
    
    # Also check for "Next" link specifically
    next_link = soup.find('a', class_=lambda x: x and 'page-numbers' in x and 'next' in x)
    if next_link and next_link.get('href'):
        href = next_link.get('href')
        if href.startswith('/'):
            full_url = BASE_URL + href
        elif href.startswith('http'):
            full_url = href
        else:
            full_url = urljoin(base_url, href)
        
        if full_url not in pagination_urls and full_url != base_url:
            if 'kuala-lumpur-selangor' in full_url.lower():
                pagination_urls.append(full_url)
                # Extract page number from next link
                page_match = re.search(r'/page/(\d+)', href, re.I)
                if page_match:
                    max_page_num = max(max_page_num, int(page_match.group(1)))
    
    # If we found a max page number, generate all page URLs up to that number
    # This handles cases where pagination shows "Page1 Page2 Page3 … Page22"
    if max_page_num > 0:
        base_path = '/category/store/kuala-lumpur-selangor'
        for page_num in range(2, min(max_page_num + 1, MAX_PAGES_PER_REGION + 1)):
            page_url = f"{BASE_URL}{base_path}/page/{page_num}/"
            if page_url not in pagination_urls:
                pagination_urls.append(page_url)
    
    # Sort URLs to process pages in order
    def extract_page_num(url):
        match = re.search(r'/page/(\d+)', url, re.I)
        return int(match.group(1)) if match else 0
    
    pagination_urls.sort(key=extract_page_num)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in pagination_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls[:MAX_PAGES_PER_REGION]  # Limit pages




def parse_location(location_text: str) -> tuple[str, str]:
    """
    Parse location text to extract district and location.
    
    Args:
        location_text: Raw location string
        
    Returns:
        Tuple of (location, district)
    """
    location_text = location_text.strip()
    
    # Common districts in KL/Selangor only
    districts = [
        "Petaling Jaya", "Kuala Lumpur", "Subang Jaya", "Klang", "Shah Alam",
        "Ampang", "Cheras", "Bangsar", "Mont Kiara", "Damansara", "Puchong",
        "Kepong", "Setapak", "Wangsa Maju", "Gombak", "Selayang", "SS 2",
        "SS2", "1 Utama", "One Utama", "Bandar Utama", "PJ", "Putrajaya",
        "Cyberjaya", "Seri Kembangan", "Kajang", "Rawang", "Port Klang",
        "Bangi", "Sepang", "Elmina", "Bandar Baru Bangi"
    ]
    
    district = None
    for d in districts:
        if d.lower() in location_text.lower():
            district = d
            break
    
    return location_text, district or "Kuala Lumpur"


def extract_outlets_from_page(soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
    """
    Extract outlet information from a single page.
    Based on actual ZUS Coffee website structure using Elementor:
    - Outlet name: <p class="elementor-heading-title">ZUS Coffee – Name</p>
    - Location region: <h2 class="location">Kuala Lumpur/Selangor</h2>
    - Address: <p> inside theme-post-content widget
    
    Args:
        soup: BeautifulSoup object of the page
        page_url: URL of the page being scraped
        
    Returns:
        List of outlet dictionaries
    """
    outlets = []
    
    # Find all outlet containers - look for elementor sections with outlet data
    # Each outlet is in a div with data-elementor-type="loop"
    outlet_containers = soup.find_all('div', {'data-elementor-type': 'loop'})
    
    if not outlet_containers:
        # Fallback: look for elementor sections that contain outlet info
        outlet_containers = soup.find_all('section', class_=lambda x: x and 'elementor-section' in x)
    
    for container in outlet_containers:
        try:
            # Find outlet name - look for elementor-heading-title with "ZUS Coffee"
            name_elem = container.find('p', class_=lambda x: x and 'elementor-heading-title' in x)
            if not name_elem:
                # Try h2/h3 with elementor-heading-title
                name_elem = container.find(['h2', 'h3'], class_=lambda x: x and 'elementor-heading-title' in x)
            
            if not name_elem:
                continue
            
            name_text = name_elem.get_text(strip=True)
            
            # Check if this is an outlet (contains "ZUS Coffee" or "ZUS")
            if 'zus' not in name_text.lower() or len(name_text) < 10:
                continue
            
            name = name_text.strip()
            
            # Find address - look for paragraph inside theme-post-content widget
            location_text = ""
            
            # Method 1: Look for theme-post-content widget
            post_content = container.find('div', class_=lambda x: x and 'theme-post-content' in str(x))
            if post_content:
                # Find paragraph with address (contains location keywords or postal code)
                paragraphs = post_content.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # Skip if it's just the entry-title span
                    if 'entry-title' in str(p.parent):
                        continue
                    # Check if it looks like an address
                    if any(keyword in text.lower() for keyword in [
                        'jalan', 'street', 'road', 'mall', 'centre', 'center', 
                        'plaza', 'selangor', 'kuala lumpur', 'floor', 'lot', 'no', 'ground'
                    ]) or re.search(r'\d{5}', text):  # Contains postal code pattern
                        location_text = text
                        break
            
            # Method 2: If no address found, look for paragraph after location heading
            if not location_text:
                location_heading = container.find('h2', class_=lambda x: x and 'location' in str(x))
                if location_heading:
                    # Find next paragraph after location heading
                    next_elem = location_heading.find_next('p')
                    if next_elem:
                        text = next_elem.get_text(strip=True)
                        if any(keyword in text.lower() for keyword in [
                            'jalan', 'street', 'road', 'mall', 'centre', 'center',
                            'plaza', 'selangor', 'kuala lumpur', 'floor', 'lot', 'no'
                        ]) or re.search(r'\d{5}', text):
                            location_text = text
            
            # Method 3: Look for any paragraph in the container with address-like content
            if not location_text:
                all_paragraphs = container.find_all('p')
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    # Skip if it's the outlet name or entry-title
                    if 'zus coffee' in text.lower() and len(text) < 100:
                        continue
                    if 'entry-title' in str(p.parent):
                        continue
                    # Check if it looks like an address
                    if any(keyword in text.lower() for keyword in [
                        'jalan', 'street', 'road', 'mall', 'centre', 'center',
                        'plaza', 'selangor', 'kuala lumpur', 'floor', 'lot', 'no', 'ground'
                    ]) or re.search(r'\d{5}', text):
                        location_text = text
                        break
            
            # If still no location, use name as fallback
            if not location_text:
                location_text = name
            
            location, district = parse_location(location_text)
            
            # Default hours (not typically shown on listing pages)
            hours = "9:00 AM - 10:00 PM"
            
            # Default services (not typically shown on listing pages)
            services = "WiFi, Dine-in"
            
            # Default coordinates (would need geocoding for real implementation)
            lat = 3.1390  # Default KL coordinates
            lon = 101.6869
            
            outlet = {
                "name": name,
                "location": location,
                "district": district,
                "hours": hours,
                "services": services,
                "lat": lat,
                "lon": lon
            }
            
            outlets.append(outlet)
            logger.debug(f"Extracted outlet: {name} - {location}")
            
        except Exception as e:
            logger.warning(f"Error parsing outlet from container: {e}")
            continue
    
    logger.info(f"Extracted {len(outlets)} outlets from page")
    return outlets


def scrape_outlets() -> List[Dict[str, Any]]:
    """
    Scrape outlets from ZUS Coffee website, page by page for KL/Selangor region.
    Source: https://zuscoffee.com/category/store/kuala-lumpur-selangor/
    
    Returns:
        List of outlet dictionaries
    """
    all_outlets = []
    seen_outlets = set()  # Track by name to avoid duplicates
    visited_urls: Set[str] = set()
    
    # Start with KL/Selangor page 1
    base_url = f"{BASE_URL}/category/store/kuala-lumpur-selangor/"
    page_urls = [base_url]
    
    try:
        # Start with page 1
        logger.info(f"Fetching initial page: {base_url}")
        response = requests.get(base_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all pagination links
        pagination_urls = find_pagination_links(soup, base_url)
        logger.info(f"Found {len(pagination_urls)} pagination pages")
        
        # Add all pagination URLs to the list
        for pag_url in pagination_urls:
            if pag_url not in page_urls:
                page_urls.append(pag_url)
        
        # Also check for "Next" link to find additional pages
        next_link = soup.find('a', string=re.compile(r'next', re.I))
        if next_link and next_link.get('href'):
            next_href = next_link.get('href')
            if next_href.startswith('/'):
                next_url = BASE_URL + next_href
            elif next_href.startswith('http'):
                next_url = next_href
            else:
                next_url = urljoin(base_url, next_href)
            
            if next_url not in page_urls and 'kuala-lumpur-selangor' in next_url.lower():
                page_urls.append(next_url)
        
        logger.info(f"Total pages to scrape: {len(page_urls)}")
        
        # Scrape each page
        for page_num, page_url in enumerate(page_urls, 1):
            if page_url in visited_urls:
                continue
            
            visited_urls.add(page_url)
            
            try:
                logger.info(f"Scraping page {page_num}/{len(page_urls)}: {page_url}")
                response = requests.get(page_url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract outlets from this page
                page_outlets = extract_outlets_from_page(soup, page_url)
                
                for outlet in page_outlets:
                    # Avoid duplicates by name
                    outlet_key = outlet['name'].lower().strip()
                    if outlet_key not in seen_outlets:
                        seen_outlets.add(outlet_key)
                        all_outlets.append(outlet)
                        logger.info(f"  ✓ Added: {outlet['name']}")
                
                # Be respectful with requests
                time.sleep(1)
                
            except requests.RequestException as e:
                logger.warning(f"Error fetching page {page_url}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error processing page {page_url}: {e}")
                continue
        
        if not all_outlets:
            logger.warning("No outlets scraped.")
            return []
        
        logger.info(f"Successfully scraped {len(all_outlets)} unique outlets from {len(visited_urls)} pages")
        return all_outlets
        
    except requests.RequestException as e:
        logger.error(f"Error fetching outlets page: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise




def save_outlets_with_retry(outlets_data: List[Dict[str, Any]], max_retries: int = 5) -> None:
    """
    Save outlets to database with retry logic for handling database locks.
    
    Args:
        outlets_data: List of outlet dictionaries to save
        max_retries: Maximum number of retry attempts
    """
    db = None
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            
            # Fetch existing outlet names to avoid duplicate checks
            existing_outlet_names = {o.name for o in db.query(Outlet.name).all()}

            new_outlets = []
            for outlet_data in outlets_data:
                if outlet_data['name'] not in existing_outlet_names:
                    new_outlets.append(Outlet(**outlet_data))
                    existing_outlet_names.add(outlet_data['name'])  # Track in memory too
                else:
                    logger.debug(f"Outlet '{outlet_data['name']}' already exists, skipping...")

            if new_outlets:
                # Batch insert in smaller chunks to reduce lock time
                batch_size = 50
                total_added = 0
                
                for i in range(0, len(new_outlets), batch_size):
                    batch = new_outlets[i:i + batch_size]
                    db.add_all(batch)
                    db.commit()
                    total_added += len(batch)
                    logger.info(f"✓ Committed batch of {len(batch)} outlets (total: {total_added}/{len(new_outlets)})")
                
                logger.info(f"✓ Added {total_added} new outlets to database")
            else:
                logger.info("No new outlets to add.")

            # Get final count
            total_count = db.query(Outlet).count()
            logger.info(f"✓ Total outlets in database: {total_count}")
            
            # Success - break out of retry loop
            break
            
        except Exception as e:
            if db:
                db.rollback()
                db.close()
                db = None
            
            error_msg = str(e).lower()
            is_locked = 'locked' in error_msg or 'database is locked' in error_msg
            
            if is_locked and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                logger.warning(f"Database locked (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Error saving outlets to database: {e}", exc_info=True)
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} attempts. Please ensure no other process is using the database.")
                raise
        finally:
            if db:
                db.close()


def main():
    """Main function to scrape and save outlets."""
    # Initialize database
    init_db()
    
    logger.info("Starting outlet scraping...")
    outlets_data = scrape_outlets()
    
    if not outlets_data:
        logger.error("No outlets scraped. Exiting.")
        sys.exit(1)
    
    # Save to database with retry logic
    save_outlets_with_retry(outlets_data)
    
    logger.info("Outlet scraping complete!")


if __name__ == "__main__":
    main()

