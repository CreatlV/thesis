from bs4 import BeautifulSoup, Comment, NavigableString, Tag
import htmlmin
from playwright.async_api import async_playwright


def clean_html(html_content):
    # Create a BeautifulSoup object and specify the parser
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script tags
    for script in soup(["script", "style", "svg", "head", "link", "meta"]):
        script.decompose()

    # Remove HTML comments
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove CSS classes
    for tag in soup(True):
        tag.attrs.pop("class", None)

    # Remove empty tags
    for tag in soup(True):
        if not tag.contents or (
            len(tag.contents) == 1
            and isinstance(tag.contents[0], NavigableString)
            and not tag.contents[0].strip()
        ):
            tag.extract()

    # Get the cleaned HTML content
    cleaned_html_content = soup.prettify()

    return cleaned_html_content


def minify_html(html_content):
    # Minify the HTML content
    minified_html_content = htmlmin.minify(html_content, remove_empty_space=True)

    return minified_html_content


async def download_html_and_text(url, use_cache=False) -> tuple[str, str]:
    TEXT_FILE = "text.html"
    HTML_FILE = "html.html"
    
    if use_cache:
      # Load the text and HTML from a file
      with open(TEXT_FILE, "r", encoding="utf-8") as file:
          visible_text = file.read()

      with open(HTML_FILE, "r", encoding="utf-8") as file:
          html_string = file.read()

      if visible_text is None or html_string is None:
                raise Exception("No text found")

      return visible_text, html_string

    try:
        # Initialize a Playwright context
        async with async_playwright() as p:
            # Launch a new browser instance
            browser = await p.chromium.launch()

            # Create a new page
            page = await browser.new_page()

            # Navigate to the URL
            await page.goto(url)

            # Evaluate JavaScript to get the text content of the body
            visible_text: str = await page.eval_on_selector("body", "body => body.innerText")

            # Get the HTML content of the page
            html_string = await page.content()

            # Close the browser
            await browser.close()

            if visible_text is None or html_string is None:
                raise Exception("No text found")

            # Save the text and HTML to a file
            with open(TEXT_FILE, "w", encoding="utf-8") as file:
                file.write(visible_text)

            with open(HTML_FILE, "w", encoding="utf-8") as file:
                file.write(html_string)

            return visible_text, html_string
    
    except Exception as e:
        print(f"An error occurred: {e}")
        raise Exception("No text found")