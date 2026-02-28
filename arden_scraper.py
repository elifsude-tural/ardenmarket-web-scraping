import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Direkt kategori sayfasına git
    driver.get("https://ardenmarket.com.tr/")
    time.sleep(4)
    wait = WebDriverWait(driver, 20)

    # Konum seç
    konum_btn = wait.until(EC.element_to_be_clickable((By.ID, "delivery-button")))
    konum_btn.click()
    time.sleep(2)
    Select(wait.until(EC.presence_of_element_located((By.ID, "delivery_state")))).select_by_value("İstanbul")
    time.sleep(2)
    ilce = Select(driver.find_element(By.ID, "delivery_city"))
    for o in ilce.options:
        if o.get_attribute("value") != "":
            ilce.select_by_value(o.get_attribute("value"))
            break
    time.sleep(2)
    mahalle = Select(driver.find_element(By.ID, "delivery_neighborhood"))
    for o in mahalle.options:
        if o.get_attribute("value") != "":
            mahalle.select_by_value(o.get_attribute("value"))
            break
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "#delivery-form button[type='submit']").click()

    # SAYFA YENİLEME YOK - form submit sonrası sayfanın kendisi güncellenecek
    print("Form gönderildi, sayfa güncelleniyor...")
    time.sleep(8)  # Daha uzun bekle

    # Şu anki URL'i göster
    print("Mevcut URL:", driver.current_url)

    # Ürün say
    items = driver.find_elements(By.CSS_SELECTOR, "li.product-item")
    print(f"Ürün sayısı: {len(items)}")

    # Hiç ürün yoksa tüm li'lerin class'larını listele
    if len(items) == 0:
        tum_li = driver.find_elements(By.TAG_NAME, "li")
        classlar = set()
        for li in tum_li:
            c = li.get_attribute("class")
            if c:
                classlar.add(c)
        print("Sayfadaki li class'ları:")
        for c in classlar:
            print(" -", c)

finally:
    driver.quit()