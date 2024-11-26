import re  # Using the standard 're' module
import json

# Enhanced regex patterns compatible with 're' module
patterns = {
    'email': r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",

    'phone': r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)*\d{3,4}",

    'fax': r"(?:Fax|F|传真|ファックス|팩스|फैक्स|тел|факс)[.:]?\s*(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)*\d{3,4}",

    'name': r"""
        (?:(?:Dr|Mr|Mrs|Ms|Miss|Professor|Prof|MD|DVM|Docteur|Vétérinaire|Asv|
        सर्व|श्री|श्रीमती|Herr|Frau|M\.|Mme|Mlle|Señor|Señora|Señorita|先生|女士|教授|博士|선생님|교수님|
        Др|Г-н|Г-жа|Господин|Госпожа|Проф)\.?\s+)?
        (?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)
    """,

    'alt_name': r"(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})",

    'address': r"""
        \d{1,5}\s+[A-Za-z0-9\s.,'-]+
    """,

    'address_fallback': r"[A-Za-z0-9\s.,'-]+",

    'social_links': {
        'facebook': r"(?:https?:\/\/)?(?:www\.)?(?:facebook|fb)\.(?:com|cn)\/[^\/\s]+\/?",
        'twitter': r"(?:https?:\/\/)?(?:www\.)?twitter\.com\/[^\/\s]+\/?",
        'instagram': r"(?:https?:\/\/)?(?:www\.)?instagram\.com\/[^\/\s]+\/?",
        'linkedin': r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:company|in)\/[^\/\s]+\/?",
        'youtube': r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:channel|user)\/[^\/\s]+\/?"
    }
}

# Compile patterns with appropriate flags
compiled_patterns = {
    'email': re.compile(patterns['email'], re.IGNORECASE),
    'phone': re.compile(patterns['phone']),
    'fax': re.compile(patterns['fax'], re.IGNORECASE),
    'name': re.compile(patterns['name'], re.VERBOSE),
    'alt_name': re.compile(patterns['alt_name']),
    'address': re.compile(patterns['address'], re.VERBOSE),
    'address_fallback': re.compile(patterns['address_fallback']),
    'social_links': {
        platform: re.compile(pattern, re.IGNORECASE)
        for platform, pattern in patterns['social_links'].items()
    }
}

def clean_phone(phone):
    """Clean phone numbers without phonenumbers library"""
    try:
        # Remove all non-digit characters
        digits = re.sub(r"\D", "", phone)

        # Return digits if length is acceptable
        if len(digits) >= 7:
            return digits
        else:
            return None  # Discard short numbers
    except Exception:
        return None

def is_likely_name(name):
    """Filter out false positives in name detection"""
    common_words = {'Home', 'Page', 'Menu', 'Contact', 'About', 'Services', 'Privacy', 'Policy',
                    'Terms', 'Conditions', 'Search', 'Main', 'Content', 'Navigation', 'Careers',
                    'Emergency', 'FAQ', 'Log', 'In', 'Out', 'Find', 'More'}
    words = name.split()
    return (
        len(words) >= 2 and
        not any(word in common_words for word in words) and
        not any(char.isdigit() for char in name) and
        all(word[0].isupper() for word in words if word)
    )

def extract_info(html):
    """Extract all contact information from HTML"""
    try:
        # Remove style and script contents
        html_no_style = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
        html_no_script = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', html_no_style, flags=re.IGNORECASE)

        # Convert HTML to text
        text_content = re.sub(r'<[^>]+>', ' ', html_no_script, flags=re.IGNORECASE)
        text_content = re.sub(r'\s+', ' ', text_content, flags=re.IGNORECASE).strip()

        # Extract emails
        emails = list(set(compiled_patterns['email'].findall(text_content)))

        # Extract and clean phone numbers
        phones = []
        phone_matches = compiled_patterns['phone'].findall(text_content)
        for phone in phone_matches:
            cleaned = clean_phone(phone)
            if cleaned and cleaned not in phones:
                phones.append(cleaned)

        # Extract and clean fax numbers
        fax_numbers = []
        fax_contexts = compiled_patterns['fax'].finditer(text_content)
        for match in fax_contexts:
            fax = clean_phone(match.group())
            if fax and fax not in fax_numbers:
                fax_numbers.append(fax)

        # Extract names
        names = set()
        titled_names = compiled_patterns['name'].findall(text_content)
        names.update(name.strip() for name in titled_names if is_likely_name(name.strip()))

        potential_names = compiled_patterns['alt_name'].findall(text_content)
        names.update(name.strip() for name in potential_names if is_likely_name(name.strip()))

        # Extract addresses using primary pattern
        addresses = list(set(compiled_patterns['address'].findall(text_content)))

        # Filter out irrelevant addresses
        addresses = [addr.strip() for addr in addresses if len(addr.strip().split()) > 2]

        # Extract all href attributes
        href_pattern = re.compile(r'href=[\'"]?([^\'" >]+)', re.IGNORECASE)
        hrefs = href_pattern.findall(html)

        # Extract social media links
        social_links = {}
        for platform, pattern in compiled_patterns['social_links'].items():
            matches = [href for href in hrefs if pattern.search(href)]
            if matches:
                social_links[platform] = list(set(matches))

        return {
            'emails': emails,
            'phones': phones,
            'fax': fax_numbers,
            'names': list(names),
            'addresses': addresses,
            'social_links': social_links
        }

    except Exception as e:
        print(f"Error in extraction: {str(e)}")
        return {
            'emails': [],
            'phones': [],
            'fax': [],
            'names': [],
            'addresses': [],
            'social_links': {}
        }

# Get HTML content from input_data provided by Zapier
html_content = input_data.get('html', '')

# Process HTML and prepare output
try:
    if not html_content:
        output = {
            'success': False,
            'error': 'No HTML content provided',
            'data': None
        }
    else:
        result = extract_info(html_content)
        output = {
            'success': True,
            'error': None,
            'data': result
        }

except Exception as e:
    output = {
        'success': False,
        'error': str(e),
        'data': None
    }

# Print the final output with required ID
print(json.dumps({
    'output': output,
    'id': '5fgunBIH5nfcaPgwiymwcjuT28AwOIJs'
}))