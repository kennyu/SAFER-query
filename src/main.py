"""
This module defines the `main()` coroutine for the Apify Actor, executed from the `__main__.py` file.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

# Beautiful Soup - library for pulling data out of HTML and XML files, read more at
# https://www.crummy.com/software/BeautifulSoup/bs4/doc
from bs4 import BeautifulSoup

# HTTPX - library for making asynchronous HTTP requests in Python, read more at https://www.python-httpx.org/
from httpx import AsyncClient

# Apify SDK - toolkit for building Apify Actors, read more at https://docs.apify.com/sdk/python
from apify import Actor


async def main() -> None:
    """
    The main coroutine is being executed using `asyncio.run()`, so do not attempt to make a normal function
    out of it, it will not work. Asynchronous execution is required for communication with Apify platform,
    and it also enhances performance in the field of web scraping significantly.
    """
    async with Actor:
        # Structure of input is defined in input_schema.json
        actor_input = await Actor.get_input() or {}
        url = "https://safer.fmcsa.dot.gov/query.asp"
        query_string = actor_input.get('query_string')

        # Create an asynchronous HTTPX client
        async with AsyncClient() as client:
            # Fill relevant params
            data = {'searchtype': 'ANY', 'query_type': 'queryCarrierSnapshot', 'query_param': 'USDOT', 'query_string': query_string}
            # Fetch the HTML content of the page.
            response = await client.post(url, data=data)
        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table with the specific href
        table = soup.find('a', href="saferhelp.aspx#InspectionsCA").find_next('table')

        # # Get the last element in the last td
        last_td = table.find_all('td')[-1]
        last_element = last_td.contents[-1].strip()

        # Save headings to Dataset - a table-like storage
        await Actor.push_data({"driver_out_of_service_percentage": last_element})
