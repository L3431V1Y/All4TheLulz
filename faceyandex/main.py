from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import shutil
import uuid
import os

app = FastAPI()

@app.post("/search/")
async def reverse_face_search(file: UploadFile = File(...)):
    temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://yandex.com/images/")
        upload_button = driver.find_element("css selector", "button[aria-label='Search by image']")
        upload_button.click()

        file_input = driver.find_element("css selector", "input[type='file']")
        file_input.send_keys(os.path.abspath(temp_filename))

        driver.implicitly_wait(8)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        result_blocks = soup.select("div.CbirSites-Item a.Link")

        results = []
        for block in result_blocks[:5]:
            href = block.get("href")
            img = block.select_one("img")
            results.append({
                "url": href,
                "thumbnail": img["src"] if img else None
            })

        return JSONResponse(content={"results": results})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        driver.quit()
        os.remove(temp_filename)
