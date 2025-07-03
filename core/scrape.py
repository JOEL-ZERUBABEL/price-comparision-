import asyncio
import json
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def amazon_scrape(query="query",output_format="json",max_pages=2):
    async with async_playwright() as p:
        try:
            browser=await p.chromium.launch(headless=False)
            context=await browser.new_context()
            page=await browser.new_page()
            await page.goto("https://www.amazon.in/")

            await page.wait_for_selector('input[name="field-keywords"]')
            await page.fill('input[name="field-keywords"]',query)
            await page.press('input[name="field-keywords"]','Enter')
            await page.wait_for_selector('div[data-component-type="s-search-result"]') 
            products=[]
            page_no=1
            while page_no<=max_pages:
                print("Scraping",page_no)

                #await page.wait_for_selector('div.sg') 
                product_elements=await page.query_selector_all('div[data-component-type="s-search-result"]')
                for product in product_elements:
                    try:
                        title_element = await product.query_selector("h2.aspan")
                        title=await title_element.inner_text() if title_element else "No Title"

                        
                        price_element=await product.query_selector("span.a-price-whole")
                        fraction_element=await product.query_selector("span.a-price-fraction")
                        price=await price_element.inner_text() if price_element else "0"
                        fraction=await fraction_element.inner_text() if fraction_element else "00"
                        full_price=f"{price}.{fraction}" if price != "0" else "Price not listed"
                        discount_element=await product.query_selector("span.a-offscreen")
                        discount=await discount_element.inner_text() if discount_element else "Nothing"
                        link_element=await product.query_selector("h2 a")
                        link="https://www.amazon.in"+await link_element.get_attribute("href") if link_element else "Nothing"
                        image_element=await product.query_selector("img")
                        image=await image_element.get_attribute("src") if image_element else ""

                        
                        products.append({
                            "title":title,
                            "price":full_price,
                            "discount":discount,
                            "picture":image,
                            "link":link,
                            "Website":"Amazon",
                        })
                 
                    except Exception as e:
                        print(f"error in extraction {e}")
                        continue
                    
                next_button=await page.query_selector("li.a-last a") 
                if not next_button:
                    break
                await next_button.click()
                await page.wait_for_selector('div[data-component-type="s-search-result"]')
                page_no+=1

            await browser.close()

            if output_format=="json":
                with open(f"{query} products.json","w",encoding='utf-8') as file:
                    json.dump(products,file,indent=4) 
                print(f"{len(products)} products saved{ query}._products{output_format}")
            return products


        except Exception as e:
            print(e)
            return []


def scrape_snapdeal(query="laptop", max_pages=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    products = []

    for page in range(1, max_pages + 1):
        url = f"https://www.snapdeal.com/search?keyword={query}&page={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        product_cards = soup.select("div.product-tuple-listing")

        if not product_cards:
            print(f"No products found on page {page}")
            break

        for card in product_cards:
            try:
                title = card.select_one("p.product-title").text.strip()
                price = card.select_one("span.product-price").text.strip()
                image = card.select_one("img.product-image")["src"]
                link = "https://www.snapdeal.com" + card.select_one("a.dp-widget-link")["href"]

                products.append({
                    "title": title,
                    "price": price,
                    "image": image,
                    "link": link,
                    "website": "Snapdeal"
                })
            except Exception as e:
                print("Error in product block:", e)
                continue

        print(f"Scraped Page {page}")


    with open(f"{query}_snapdeal_products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=4)

    print(f"Scraped {len(products)} products from Snapdeal")
    return products


if __name__ == "__main__":
    query = input("Enter the product to search: ")

    async def run_all_scrapers():
        amazon_data = await amazon_scrape(query)
        snapdeal_data = await scrape_snapdeal(query)
        
        all_data = amazon_data + snapdeal_data
        
        if all_data:
            print(f"\nScraped{len(all_data)} products for '{query}':\n")
            for product in all_data:
                print(product)
        else:
            print("No products found from any website.")

    asyncio.run(run_all_scrapers(query))
 