from __future__ import annotations  # noqa: D100

import os  # noqa: D100
from typing import Callable, Dict, List

import requests
from prettytable import ALL, PrettyTable
from tiktoken import get_encoding
from tqdm import tqdm


def count_tokens(input_string: str) -> int:  # noqa: D417
    """Counts the number of tokens in the input string.

    Parameters
    ----------
    input_string (str): The input string to count tokens from.

    Returns
    -------
    int: The number of tokens in the input string.

    """  # noqa: D401
    tokenizer = get_encoding("cl100k_base")
    tokens = tokenizer.encode(input_string)
    return len(tokens)


def calculate_cost(input_string: str, cost_per_million_tokens: float = 5) -> float:
    """Calculates the cost of processing an input string based on the number of tokens.

    Args:
        input_string (str): The input string to be processed.
        cost_per_million_tokens (float, optional): The cost per million tokens. Defaults to 5.

    Returns:
        float: The total cost of processing the input string.

    """  # noqa: D401, E501
    num_tokens = count_tokens(input_string)
    return (num_tokens / 1_000_000) * cost_per_million_tokens


def scrape_jina_ai(url: str) -> str:
    """Scrapes the content of a webpage from the Jina AI website.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        str: The scraped content of the webpage.

    """
    response = requests.get("https://r.jina.ai/" + url)  # noqa: S113
    return response.text


list_of_scraper_functions = [
    {"name": "Jina AI", "function": scrape_jina_ai}
]


def view_scraped_content2(
        scrape_url_functions: List[Dict[str, Callable[[str], str]]],
        sites_list: List[Dict[str, str]],
        characters_to_display: int = 500,
        table_max_width: int = 50) -> List[Dict[str, str]]:
    """View the scraped content from multiple websites using different scraping functions.

    Args:
        scrape_url_functions (List[Dict[str, Callable[[str], str]]]): A list of dictionaries containing the name and
            function of the scraping functions to be used.
        sites_list (List[Dict[str, str]]): A list of dictionaries containing the name and URL of the websites to be scraped.
        characters_to_display (int, optional): The number of characters to display for each scraped content. Defaults to 500.
        table_max_width (int, optional): The maximum width of the content and cost tables. Defaults to 50.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the scraped data for each website and scraping function.
            Each dictionary contains the provider name and a list of sites with their corresponding scraped content.

    Raises:
        None

    """  # noqa: E501
    content_table_headers = ["Site Name"] + [f"{func["name"]} content" for func in scrape_url_functions]
    cost_table_headers = ["Site Name"] + [f"{func["name"]} cost" for func in scrape_url_functions]

    content_table = PrettyTable()
    content_table.field_names = content_table_headers

    cost_table = PrettyTable()
    cost_table.field_names = cost_table_headers

    scraped_data = []

    raw_data_dir = "/Users/nicorod/Documents/repos/Chatbot-Fonasa/data/raw"
    os.makedirs(raw_data_dir, exist_ok=True)

    for site in sites_list:
        content_row = [site["name"]]
        cost_row = [site["name"]]
        site_data = {"provider": site["name"], "sites": []}

        for scrape_function in scrape_url_functions:
            function_name = scrape_function["name"]
            for _ in tqdm([site], desc=f"Processing site {site["name"]} using {function_name}"):
                try:
                    content = scrape_function["function"](site["url"])
                    content_snippet = content[:characters_to_display]
                    content_row.append(content_snippet)

                    cost = calculate_cost(content)
                    cost_row.append(f"${cost:.6f}")

                    site_data["sites"].append({"name": function_name, "content": content})

                    filename = os.path.join(raw_data_dir, f"{site["name"].replace(" ", "_")}_{function_name}.txt")
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Successfully saved content to {filename}")
                except Exception as e:  # noqa: PERF203
                    error_message = f"Error: {e!s}"
                    content_row.append(error_message)
                    cost_row.append("Error")

                    site_data["sites"].append({"name": function_name, "content": error_message})
                    print(f"Failed to process site {site["name"]} using {function_name}: {e}")  # noqa: T201
                    continue

        content_table.add_row(content_row)
        cost_table.add_row(cost_row)
        scraped_data.append(site_data)

    content_table.max_width = table_max_width
    content_table.hrules = ALL

    cost_table.max_width = table_max_width
    cost_table.hrules = ALL

    print("Content Table:")  # noqa: T201
    print(content_table)  # noqa: T201

    print("\nCost Table:\nThis is how much it would cost to use GPT-4 to parse this content for extraction.")  # noqa: T201
    print(cost_table)  # noqa: T201

    return scraped_data
