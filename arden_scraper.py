from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas as pd
import csv




# 1. Chrome Tarayıcı Ayarları
options = webdriver.ChromeOptions()
# options.add_argument("--headless") # Tarayıcı penceresini görmemek istersen bunu açabilirsin

# 2. Sürücüyü otomatik kur ve başlat
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 3. Arden Market'e git
    print("Siteye gidiliyor...")
    driver.get("https://ardenmarket.com.tr/et-ve-tavuk.html")

    # Sayfanın yüklenmesi için 5 saniye bekle
    time.sleep(5)

    urunler = driver.find_elements(By.CLASS_NAME, "product-item")

    print(f"Toplam{len(urunler)} urun bulundu.\n")


    with open('arden_products.csv', mode='w', newline='', encoding='utf-8-sig') as csvfile:
        yazici = csv.writer(csvfile)

        yazici.writerow(['Product Name','Price'])

        for urun in urunler:
            try:
                isim = urun.find_element(By.CSS_SELECTOR, "strong.product-item-name").text

                fiyat = urun.find_element(By.CSS_SELECTOR, "span.price").text

                yazici.writerow([isim, fiyat])

                print(f"Urun: {isim} | Fiyat: {fiyat}")
            except:
                continue

    #input("\nVerileri gorduysen Enter'a basarak tarayiciyi kapatabilirsin...")
    print("Successfully made a csv file.")



finally:
    # İşlem bitince tarayıcıyı kapat

    driver.quit()
