import os
import pandas as pd
import openai
from openai import OpenAI  # Correct import for OpenAI class
import tkinter as tk
from tkinter import filedialog, messagebox
from azure.cognitiveservices.search.websearch import WebSearchClient
from msrest.authentication import CognitiveServicesCredentials
from urllib.parse import urlparse, urlunparse, urljoin
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import requests
from bs4 import BeautifulSoup
import time

# Replace with your API keys
openai.api_key = "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"  # OpenAI API Key
BING_API_KEY = "464f51adb78a47c2be5eaaf9a2b503f0"      # Bing Web Search API Key

# Initialize OpenAI client
client = OpenAI(api_key=openai.api_key)

# Function to generate search queries using OpenAI
def generate_search_query(missing_column, row_data):
    context = ''
    for col, val in row_data.items():
        if col != missing_column and pd.notna(val) and val != '':
            context += f"{col}: {val}\n"

    if not context:
        return None

    prompt = f"""You are a helpful assistant. Given the following information, generate a concise search query to find the '{missing_column}':

{context}

Search Query:"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            n=1,
            temperature=0.5,
        )
        query = completion.choices[0].message.content.strip()
        return query
    except Exception as e:
        print(f"Error generating search query: {e}")
        return None

# Function to perform web search using Bing Web Search API
def perform_web_search(query):
    try:
        client_bing = WebSearchClient(
            endpoint="https://api.bing.microsoft.com/v7.0",  # Ensure the correct endpoint
            credentials=CognitiveServicesCredentials(BING_API_KEY)
        )
        web_data = client_bing.web.search(query=query)
        if web_data.web_pages:
            # Get URLs of the top 10 search results
            urls = [page.url for page in web_data.web_pages.value[:10]]
            return urls
        else:
            return []
    except Exception as e:
        print(f"Error performing web search: {e}")
        return []

# Function to modify the query for retries
def modify_query(query):
    # Simple modification: remove quotes and extra words
    query = query.replace('"', '').strip()
    # Further modifications can be added as needed
    return query

# Function to perform web search with retry mechanism
def perform_web_search_with_retry(query, max_retries=2):
    for attempt in range(max_retries):
        urls = perform_web_search(query)
        if urls:
            return urls
        else:
            print(f"   No search results found for '{query}'.")
            if attempt < max_retries - 1:
                print(f"   Modifying query and retrying...")
                query = modify_query(query)
            else:
                print(f"   All retries exhausted for query '{query}'. Skipping...")
    return []

# Function to fetch HTML body from a URL
def fetch_html_body(url):
    headers = {
        'User-Agent': (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error fetching HTML body: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching HTML body: {e}")
        return None

# Function to extract image URLs from HTML content
def extract_image_urls(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    image_urls = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            image_url = urljoin(base_url, src)
            image_urls.append(image_url)
    return image_urls

# Function to download image from URL
def download_image(image_url):
    headers = {
        'User-Agent': (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
    }
    try:
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content  # Return image bytes
    except Exception as e:
        print(f"Error downloading image '{image_url}': {e}")
        return None

# Function to perform reverse image search using Bing Visual Search API
def perform_reverse_image_search(image_bytes):
    endpoint = 'https://api.bing.microsoft.com/v7.0/images/visualsearch'
    headers = {
        'Ocp-Apim-Subscription-Key': BING_API_KEY,
    }
    files = {
        'image': ('image.jpg', image_bytes, 'multipart/form-data')
    }
    try:
        response = requests.post(endpoint, headers=headers, files=files, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error performing reverse image search: {e}")
        return None

# Function to extract image description from Visual Search API response
def extract_image_description(visual_search_response):
    descriptions = []
    tags = visual_search_response.get('tags', [])
    for tag in tags:
        display_name = tag.get('displayName', '')
        if display_name:
            descriptions.append(display_name)
        actions = tag.get('actions', [])
        for action in actions:
            action_type = action.get('actionType', '')
            if action_type == 'PagesIncluding':
                for value in action.get('data', {}).get('value', []):
                    snippet = value.get('snippet', '')
                    if snippet:
                        descriptions.append(snippet)
    return ' '.join(descriptions)

# Function to extract required information using OpenAI
def extract_information(missing_column, html_contents):
    # Combine all HTML contents
    combined_text = ' '.join(html_contents)

    prompt = f"""Based on the following web page content and image descriptions, extract the '{missing_column}'. If the information is not found, reply with 'Not found'.
    
Web Content and Image Descriptions:
{combined_text}

{missing_column}:"""

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            n=1,
            temperature=0.3,
        )
        result = completion.choices[0].message['content'].strip()
        return result
    except Exception as e:
        print(f"Error extracting information: {e}")
        return None

# Function to fill missing information in a DataFrame
def fill_missing_info(df):
    headers = df.columns.tolist()
    print(f"Headers: {headers}")
    total_rows = len(df)
    for index, row in df.iterrows():
        row_data = row.to_dict()
        print(f"\nProcessing row {index+1}/{total_rows}")
        for column in headers:
            if pd.isna(row[column]) or row[column] == '':
                print(f" - Missing '{column}', generating search query...")
                # Step 1: Generate search query
                query = generate_search_query(column, row_data)
                if not query:
                    print(f"   Error generating search query for '{column}'. Skipping...")
                    continue
                print(f"   Search query: {query}")

                # Step 2: Perform web search with retry and get URLs
                urls = perform_web_search_with_retry(query)
                if not urls:
                    print(f"   No search results found for '{query}'. Skipping...")
                    continue
                print(f"   Retrieved URLs: {urls}")

                # Step 3: Fetch HTML bodies from URLs and process images
                html_contents = []
                for url in urls:
                    print(f"   Fetching content from URL: {url}")
                    html_content = fetch_html_body(url)
                    if html_content:
                        html_contents.append(html_content)

                        # Extract image URLs
                        image_urls = extract_image_urls(html_content, url)
                        if image_urls:
                            # Limit the number of images to process per page
                            image_urls = image_urls[:3]
                            for image_url in image_urls:
                                print(f"   Processing image: {image_url}")
                                image_bytes = download_image(image_url)
                                if image_bytes:
                                    visual_search_response = perform_reverse_image_search(image_bytes)
                                    if visual_search_response:
                                        # Extract image description
                                        image_description = extract_image_description(visual_search_response)
                                        if image_description:
                                            # Add image description to html_contents
                                            html_contents.append(image_description)
                                time.sleep(1)  # Be polite and avoid rapid requests

                    time.sleep(1)  # Be polite and avoid rapid requests

                if not html_contents:
                    print(f"   No content fetched from URLs. Skipping...")
                    continue

                # Step 4: Extract information using OpenAI
                print(f"   Extracting '{column}' from web content and image descriptions...")
                extracted_info = extract_information(column, html_contents)
                if extracted_info and extracted_info.lower() != 'not found':
                    df.at[index, column] = extracted_info
                    print(f"   Filled '{column}' with: {extracted_info}")
                else:
                    print(f"   Could not extract '{column}' for row {index+1}.")
    return df

# Function to process each Excel file
def process_excel_file(input_path, output_path):
    try:
        # Read the Excel file and ensure the first row is the header
        df = pd.read_excel(input_path, header=0)
        
        # Remove any formatting and special designs
        df.columns = df.columns.str.strip()
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        
        # Drop columns that do not need to be analyzed
        # Drop columns that do not need to be analyzed
        columns_to_exclude = ['Company owner', 'Civilty', 'Contact first name', 'Contact last name', 'Position', 'Comments', '(Hyperline) Assign a subscription link', '(Hyperline) Billing email', '(Hyperline) Create a new invoice link', '(Hyperline) Currency', '(Hyperline) Custom payment delay (in days)', '(Hyperline) Custom tax rate', '(Hyperline) Estimated ARR', '(Hyperline) External ID', '(Hyperline) ID', '(Hyperline) Invoice emails (comma separated)', '(Hyperline) Language', '(Hyperline) Next payment amount', '(Hyperline) Next payment date', '(Hyperline) Open invoices link', '(Hyperline) Open link', '(Hyperline) Open subscriptions link', '(Hyperline) Synchronize', '(Hyperline) Tax number', '(Hyperline) Timezone', 'About Us', 'Annual Revenue', 'Campaign of last booking in meetings tool', 'City', 'Clinic email', 'Close Date', 'Company Domain Name', 'Company Keywords', 'Company name', 'Company Type', 'Corporate group', 'Country/Region', 'Country/Region Code', 'Create Date', 'Created by user ID', 'Date of last meeting booked in meetings tool', 'Days to Close', 'Description', 'Employee range', 'Employees on LinkedIn', 'Existing CT?', 'Facebook Company Page', 'Facebook Fans', 'First Contact Create Date', 'First Conversion', 'First Conversion Date', 'First Deal Created Date', 'First Touch Converting Campaign', 'Founded on', 'Google Plus Page', 'Has been enriched', 'Has Org Chart', 'Headquarter', 'HubSpot Team', 'Ideal Customer Profile Tier', 'Industry', 'Industry group', 'Is Public', 'Last Activity Date', 'Last Booked Meeting Date', 'Last Contacted', 'Last Engagement Date', 'Last Logged Call Date', 'Last Modified Date', 'Last Open Task Date', 'Last Touch Converting Campaign', 'Latest Traffic Source', 'Latest Traffic Source Data 1', 'Latest Traffic Source Data 2', 'Latest Traffic Source Timestamp', 'Lead Status', 'LF MRI / HF MRI / CT Scan', 'Lifecycle Stage', 'LinkedIn Bio', 'LinkedIn Company Page', 'Linkedin handle', 'LinkedIn url', 'Logo URL', 'Medium of last booking in meetings tool', 'Merged Company IDs', 'MRI Field Strength 1', 'MRI Field Strength 2', 'MRI Manufacturer 1', 'MRI Manufacturer 2', 'MRI Model 1', 'MRI Model 2', 'MRI quantity', 'MRI Type', 'MRI?', 'Next Activity Date', 'Number of Associated Contacts', 'Number of Associated Deals', 'Number of blockers', 'Number of child companies', 'Number of Contacts on Org Chart', 'Number of contacts with a buying role', 'Number of decision makers', 'Number of Employees', 'Number of Form Submissions', 'Number of HubSpot Contacts on Org Chart', 'Number of open deals', 'Number of Pageviews', 'Number of Placeholder Contacts on Org Chart', 'Number of Sessions', 'Number of times contacted', 'Org Chart Last Updated At', 'Original Traffic Source', 'Original Traffic Source Drill-Down 1', 'Original Traffic Source Drill-Down 2', 'Owner assigned date', 'Ownership Type', 'PARENT ACCOUNT', 'Parent Company', 'Phone Number', 'Postal Code', 'Practice Type', 'Recent Conversion', 'Recent Conversion Date', 'Recent Deal Amount', 'Recent Deal Close Date', 'Record source', 'Record source detail 1', 'Record source detail 2', 'Record source detail 3', 'Revenue range', 'Size', 'Source of last booking in meetings tool', 'Specialities', 'State/Region', 'Street Address', 'Street Address 2', 'Sync ID', 'Tagline', 'Target Account', 'Time First Seen', 'Time Last Seen', 'Time of First Session', 'Time of Last Session', 'Time Zone', 'Total Money Raised', 'Total open deal value', 'Total Revenue', 'Twitter Bio', 'Twitter Followers', 'Twitter Handle', 'Type', 'Updated by user ID', 'VET/CRO/BIO/MED/Academia (Cloned)', 'Web Technologies', 'Website URL', 'Year Founded', 'Additional Domains']

        df = df.drop(columns=columns_to_exclude, errors='ignore')
        
        # Fill missing information
        df_filled = fill_missing_info(df)
        
        # Save the processed DataFrame to a new Excel file
        df_filled.to_excel(output_path, index=False)
        print(f"\nProcessed and saved: {output_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

# GUI Functions
def select_input_folder():
    folder_selected = filedialog.askdirectory()
    input_folder_var.set(folder_selected)

def select_output_folder():
    folder_selected = filedialog.askdirectory()
    output_folder_var.set(folder_selected)

def start_processing():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()

    if not input_folder or not output_folder:
        messagebox.showwarning("Input Required", "Please select both input and output folders.")
        return

    # Process all Excel files in the input folder
    for filename in os.listdir(input_folder):
        if (filename.endswith('.xlsx') or filename.endswith('.xls')) and not filename.startswith('~$'):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)
            print(f"\nProcessing file: {filename}")
            process_excel_file(input_file_path, output_file_path)
        else:
            print(f"Skipping file: {filename}")

    messagebox.showinfo("Processing Complete", "All files have been processed.")

# Set up the GUI
root = tk.Tk()
root.title("CRM Data Updater")

input_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()

tk.Label(root, text="Select Input Folder:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=input_folder_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Browse", command=select_input_folder).grid(row=0, column=2, padx=10)

tk.Label(root, text="Select Output Folder:").grid(row=1, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=1, column=1)
tk.Button(root, text="Browse", command=select_output_folder).grid(row=1, column=2, padx=10)

tk.Button(root, text="Start Processing", command=start_processing).grid(row=2, column=0, columnspan=3, pady=20)

root.mainloop()