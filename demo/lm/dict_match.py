from lxml import html, etree
import re


def get_html_xpath_from_dict(dict, html_string, keys_to_ignore=[]):
    xpath_dict: dict[str, str] = {}

    # Parse the HTML
    tree = html.fromstring(html_string)
    et = etree.ElementTree(tree)

    # Loop over each key in the dictionary
    for key in dict:
        if key in keys_to_ignore:
            continue
        # Get all elements in the HTML
        for element in tree.iter():
            
            if isinstance(dict[key], list):
                continue

            # If the text of the element matches the key, ignore any whitespace in the HTML
            search = re.sub(r"\s+", "", str(dict[key]))
            pattern_string = r'\s*'.join(re.escape(c) for c in search)
            pattern = re.compile(pattern_string)
            if element.text_content() is not None and bool(
                pattern.search(element.text_content())
            ):
                # Add the XPath of the element to the dictionary
                xpath_dict[key] = et.getpath(element)

    return xpath_dict
