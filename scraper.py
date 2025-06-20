import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

visited = set()  # Keep track of visited URLs
count = 0  # Counter for URLs

def clean_text(text):
    """Cleans and formats extracted text."""
    lines = text.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines and extra spaces
    return "\n".join(cleaned_lines)

def get_all_links(base_url, filename="scraped_content.txt"):
    """Scrapes all sub-URLs from a given website and stores content."""
    global count

    if base_url in visited:  # Prevent revisiting the same URL
        return
    
    visited.add(base_url)  # Mark URL as visited

    try:
        print(f"Fetching: {base_url}")
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Open file in "write" mode to clear old content before writing new data
        if count == 0:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(f"Scraped Data from {base_url}\n{'='*100}\n")

        count += 1
        print(f"{count}. {base_url}")  # Print URL in terminal
        save_content(base_url, filename)  # Fetch and save content

        # Extract all links from the page
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            parsed_url = urlparse(url)

            # Skip image links or binary file links (based on extensions)
            if any(url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.pdf', '.mp4']):
                continue

            # Ensure the URL is within the same domain and has not been visited
            if parsed_url.netloc == urlparse(base_url).netloc and url not in visited:
                get_all_links(url, filename)  # Recursive call for sub-links

    except Exception as e:
        print(f"Error: {e}")

def save_content(url, filename):
    """Fetches and saves clean text content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove unwanted elements (scripts, styles, etc.)
        for script_or_style in soup(['script', 'style', 'header', 'footer', 'noscript', 'img']):
            script_or_style.decompose()  # Remove non-visible content

        # Extract only visible text from body and paragraphs
        visible_text = soup.get_text(separator="\n")

        # Clean the visible text (remove extra spaces, line breaks, etc.)
        cleaned_text = clean_text(visible_text)

        # Check for valid, readable text before saving
        if cleaned_text.strip():
            try:
                # Attempt to encode the text to handle encoding issues
                cleaned_text.encode('utf-8')
                with open(filename, "a", encoding="utf-8") as file:  # Append content instead of overwriting
                    file.write(f"\n{'='*100}\n")
                    file.write(f"URL: {url}\n")
                    file.write(f"{'='*100}\n")
                    file.write(cleaned_text + "\n\n")
                print(f"✔ Content saved for: {url}")
            except UnicodeEncodeError as e:
                print(f"⚠ Skipping {url}: Contains non-encodable characters. Error: {e}")
        else:
            print(f"⚠ Content for {url} is empty or unreadable. Skipping...")

    except Exception as e:
        print(f"Error fetching content from {url}: {e}")

if __name__ == "__main__":
    website = input("Enter the website URL to scrape: ").strip()
    print("\nScraping URLs and fetching content...\n")
    get_all_links(website)
    print(f"\nScraping completed! Total unique URLs found: {len(visited)}. Content saved in 'scraped_content.txt'.")
