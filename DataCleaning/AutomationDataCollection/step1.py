import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup

# Check urllib3 version to set the correct parameter
try:
    import urllib3
    urllib3_version = urllib3.__version__
except ImportError:
    # Default to an older version if urllib3 is not available
    urllib3_version = '1.25.0'

# Define the Retry class with the appropriate argument
def get_retry():
    from urllib3.util import Retry
    if urllib3_version >= '1.26.0':
        return Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
    else:
        return Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST"]
        )

# Get the URL from the input data
url = input_data.get('url', '').strip()

# Clean the URL to remove any unwanted characters like '\r' and '\n'
parsed_url = urlparse(url)
clean_path = parsed_url.path.replace('\r', '').replace('\n', '')
clean_url = urlunparse(parsed_url._replace(path=clean_path))

headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    )
}

# Set up a session with retry strategy
session = requests.Session()

retry_strategy = get_retry()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount('http://', adapter)
session.mount('https://', adapter)

try:
    # Fetch the HTML content with a timeout
    response = session.get(clean_url, headers=headers, timeout=5)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the entire content of the <body> tag, including all HTML
    body_tag = soup.body
    if body_tag:
        body_html = str(body_tag)
    else:
        body_html = ''

    # Output the body HTML
    output = {'html': body_html.strip()}

except requests.exceptions.RequestException as e:
    output = {'error': f'Error fetching URL: {e}'}

# For demonstration purposes, print the output
print(output)