from typing import Optional
from bs4 import BeautifulSoup
from lxml import html, etree
import re

def remove_extra_spaces(text):
    text_without_extra_spaces = re.sub(' +', ' ', text)
    return text_without_extra_spaces.strip()

def extract_data_from_html(xpath_dict: dict[str, str], html_file_path: Optional[str] = None, html_string: Optional[str] = None):
    
  
    if html_file_path is not None and html_string is not None:
        raise Exception("Only one of html_file_path or html_string must be provided")
    
    if html_file_path is not None:
      # Read the HTML file
      with open(html_file_path, "r", encoding="utf-8") as file:
          html_content = file.read()
    else:
      html_content = html_string

    if html_content is None:
        raise Exception("No HTML content found")


    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")
    html_content = soup.prettify()

    # Parse the HTML content with lxml
    html_tree = etree.HTML(html_content) # type: ignore

    # Create a dictionary to hold the extracted data
    extracted_data = {}

    # Extract data from HTML nodes using the provided XPaths
    for key, value in xpath_dict.items():
        nodes = html_tree.xpath(value)
        if nodes:
            # Get all the text content of the node and its subnodes
            subnode_text = " ".join(
                [" ".join(node.xpath(".//text()")) for node in nodes]
            )
            # Save it in the dictionary
            # Remove extra whitespace and newlines
            extracted_data[key] = (
                remove_extra_spaces(subnode_text.replace("\n", " ")
                .replace("\r", " ")
                .replace("\t", " "))
                
            )

    return extracted_data