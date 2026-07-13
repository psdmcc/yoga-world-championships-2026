import asyncio
import json
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

class MultiChannelYogaScraper:
    def __init__(self):
        self.search_query = "World Yogasana Championship 2026"
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        self.results = []

    async def scrape_news_channels(self):
        print("📰 Scraping Global News Networks...")
        search_url = f"https://duckduckgo.com{self.search_query.replace(' ', '+')}"
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                response = await client.get(search_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                for item in soup.find_all('div', class_='result__body'):
                    title_elem = item.find('a', class_='result__url')
                    snippet_elem = item.find('a', class_='result__snippet')
                    if title_elem and snippet_elem:
                        self.results.append({
                            "Channel": "News Media",
                            "Timestamp": datetime.now().isoformat(),
                            "Title": title_elem.text.strip(),
                            "URL": title_elem['href'],
                            "Content": snippet_elem.text.strip()
                        })
                print(f"txt: News engine completed. Found {len(self.results)} entries.")
            except Exception as e:
                print(f"err: News engine failed: {e}")

    async def scrape_social_and_video_channels(self):
        print("📹 Spinning up Headless Browser for Dynamic Channels (YouTube/Instagram)...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            yt_url = f"https://youtube.com{self.search_query.replace(' ', '+')}"
            try:
                await page.goto(yt_url, wait_until="networkidle")
                for _ in range(3):
                    await page.mouse.wheel(0, 4000)
                    await asyncio.sleep(1.5)
                video_elements = await page.locator("ytd-video-renderer").all()
                for video in video_elements:
                    title_text = await video.locator("#video-title").text_content()
                    link_href = await video.locator("#video-title").get_attribute("href")
                    desc_text = await video.locator("#description-text").text_content()
                    if title_text:
                        self.results.append({
                            "Channel": "YouTube Broadcast Log",
                            "Timestamp": datetime.now().isoformat(),
                            "Title": title_text.strip(),
                            "URL": f"https://youtube.com{link_href}",
                            "Content": desc_text.strip() if desc_text else "None"
                        })
                print("txt: Video/Social tracking engine completed successfully.")
            except Exception as e:
                print(f"err: Dynamic engine failed: {e}")
            finally:
                await browser.close()

    async def run_pipeline(self):
        await asyncio.gather(
            self.scrape_news_channels(),
            self.scrape_social_and_video_channels()
        )
        with open("data/yogasana_championships_master.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
        df = pd.DataFrame(self.results)
        df.to_csv("data/yogasana_championships_master.csv", index=False)
        print(f"\nPipeline Complete! {len(df)} total data fields exported.")

if __name__ == "__main__":
    scraper = MultiChannelYogaScraper()
    asyncio.run(scraper.run_pipeline())
