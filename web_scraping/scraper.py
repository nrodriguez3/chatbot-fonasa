import os
import requests
from typing import List, Dict
from tqdm import tqdm
from jina import Flow

def scrape_jina_ai(url: str) -> str:
    """Scrapes the content of a webpage and converts it to markdown using Jina AI.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        str: The scraped content in markdown format.
    """
    # Configure Flow with rate limiting and timeout
    flow = Flow().config_gateway(
        protocol='http',
        prefetch=2,  # Limit to 2 parallel requests
        timeout_send=5000  # 5 second timeout
    )
    
    with flow:
        response = requests.get("https://r.jina.ai/" + url)
        return response.text

def save_url_content(sites_list: List[Dict[str, str]], base_dir: str) -> None:
    """Scrapes content from URLs using Jina AI and saves them as txt files.
    
    Args:
        sites_list: List of dictionaries containing 'name', 'url', and 'folder' keys
                Example: [{'name': 'Page Name', 'url': 'https://example.com', 'folder': 'docs'}]
        base_dir: Base directory where subfolders will be created
    """
    # Create base directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)
    
    # Process each site
    for site in tqdm(sites_list, desc="Processing URLs"):
        try:
            # Create subfolder path and ensure it exists
            subfolder_path = os.path.join(base_dir, site['folder'])
            os.makedirs(subfolder_path, exist_ok=True)
            
            # Get markdown content using Jina
            content = scrape_jina_ai(site['url'])
            
            # Generate filename from site name
            filename = site['name'].replace(' ', '_').replace('/', '_').replace('\\', '_')
            if not filename.endswith('.txt'):
                filename += '.txt'
                
            # Save content to file
            file_path = os.path.join(subfolder_path, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"Successfully saved: {file_path}")
                
        except Exception as e:
            print(f"Error processing {site['url']}: {str(e)}")
            continue