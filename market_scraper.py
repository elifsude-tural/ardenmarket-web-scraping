import time
import csv
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 20)

KATEGORILER = [
    "https://ardenmarket.com.tr/et-ve-tavuk.html",
    "https://ardenmarket.com.tr/meyve-ve-sebze.html",
    "https://ardenmarket.com.tr/kahvaltilik.html",
    "https://ardenmarket.com.tr/sut-urunleri.html",
    "https://ardenmarket.com.tr/temel-gida.html",
    "https://ardenmarket.com.tr/dondurulmus-urunler.html",
    "https://ardenmarket.com.tr/unlu-mamul-tatli.html",
    "https://ardenmarket.com.tr/dondurma.html",
    "https://ardenmarket.com.tr/atistirmalik.html",
    "https://ardenmarket.com.tr/icecekler.html",
    "https://ardenmarket.com.tr/temizlik-urunleri.html",
    "https://ardenmarket.com.tr/kisisel-bakim.html",
    "https://ardenmarket.com.tr/bebek.html",
    "https://ardenmarket.com.tr/evcil-hayvan-urunleri.html",
    "https://ardenmarket.com.tr/ev-yasam-oyuncak.html",
    "https://ardenmarket.com.tr/ofis-ve-teknoloji.html",
    "https://ardenmarket.com.tr/firsat-urunleri.html",
    "https://ardenmarket.com.tr/catalog/category/view/s/sarkuteri-urunleri/id/4463/",
]

tum_urunler = []


# ─────────────────────────────────────────────
# YARDIMCI: Overlay varsa kaldır (JS ile)
# ─────────────────────────────────────────────
def overlay_kaldir():
    try:
        driver.execute_script("""
            var overlay = document.getElementById('ln_overlay');
            if (overlay) overlay.style.display = 'none';
            // Genel modal/overlay temizliği
            document.querySelectorAll('[class*="overlay"],[class*="modal"],[id*="overlay"]')
                .forEach(function(el){ el.style.display='none'; });
        """)
    except:
        pass


# ─────────────────────────────────────────────
# JS ile güvenli tıklama (overlay bypass)
# ─────────────────────────────────────────────
def js_click(element):
    driver.execute_script("arguments[0].click();", element)


# ─────────────────────────────────────────────
# Konum seçimi
# ─────────────────────────────────────────────
def konum_sec():
    driver.get("https://ardenmarket.com.tr/")
    time.sleep(6)

    konum_btn = None
    btn_selectors = [
        (By.ID, "delivery-button"),
        (By.CSS_SELECTOR, "[id*='delivery']"),
        (By.CSS_SELECTOR, "button[class*='delivery']"),
        (By.XPATH, "//button[contains(text(),'Konum') or contains(text(),'Teslimat') or contains(text(),'Adres')]"),
        (By.CSS_SELECTOR, ".delivery-button"),
    ]

    for by, selector in btn_selectors:
        try:
            konum_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((by, selector)))
            print(f"  ✅ Konum butonu bulundu: {by}={selector}")
            break
        except:
            continue

    if konum_btn is None:
        print("  ⚠️  Konum butonu bulunamadı, devam ediliyor...")
        return

    js_click(konum_btn)
    time.sleep(3)

    try:
        state_select = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "delivery_state"))
        ))
        for o in state_select.options:
            if "stanbul" in o.text:
                state_select.select_by_value(o.get_attribute("value"))
                break
        else:
            state_select.select_by_index(1)
        time.sleep(2)
    except Exception as e:
        print(f"  ⚠️  İl seçimi hatası: {e}")

    try:
        ilce = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "delivery_city"))
        ))
        for o in ilce.options:
            if o.get_attribute("value") != "":
                ilce.select_by_value(o.get_attribute("value"))
                break
        time.sleep(2)
    except Exception as e:
        print(f"  ⚠️  İlçe seçimi hatası: {e}")

    try:
        mahalle = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "delivery_neighborhood"))
        ))
        for o in mahalle.options:
            if o.get_attribute("value") != "":
                mahalle.select_by_value(o.get_attribute("value"))
                break
        time.sleep(2)
    except Exception as e:
        print(f"  ⚠️  Mahalle seçimi hatası: {e}")

    try:
        for sel in ["#delivery-form button[type='submit']", "form button[type='submit']", "button[type='submit']"]:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, sel)
                js_click(btn)
                break
            except:
                continue
    except Exception as e:
        print(f"  ⚠️  Submit hatası: {e}")

    print("✅ Konum seçildi")
    time.sleep(8)


# ─────────────────────────────────────────────
# Scroll
# ─────────────────────────────────────────────
def scroll_to_bottom():
    onceki = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        yeni = driver.execute_script("return document.body.scrollHeight")
        if yeni == onceki:
            break
        onceki = yeni


# ─────────────────────────────────────────────
# Son sayfa numarasını al
# DÜZELTME: Her tıklamada element yeniden bulunuyor (StaleElement fix)
# DÜZELTME: Hata durumunda base_url'e dönülüyor
# ─────────────────────────────────────────────
def son_sayfa_numarasini_al(base_url):
    def sayfadaki_max_numara():
        numaralar = []
        elems = driver.find_elements(By.CSS_SELECTOR, ".pages-items .item a, .pages-items .item strong")
        for e in elems:
            try:
                numaralar.append(int(e.text.strip()))
            except:
                pass
        for e in driver.find_elements(By.CSS_SELECTOR, "a[href*='?p=']"):
            href = e.get_attribute("href") or ""
            m = re.search(r'\?p=(\d+)', href)
            if m:
                numaralar.append(int(m.group(1)))
        return max(numaralar) if numaralar else 1

    def sonraki_btn_href():
        """
        Elementi döndürmek yerine sadece href döndürüyoruz.
        Bu sayede StaleElementReference hatası olmaz.
        """
        try:
            overlay_kaldir()  # Önce overlay'i temizle
            btns = driver.find_elements(By.CSS_SELECTOR, ".pages-items .item.pages-item-next a")
            if btns:
                href = btns[0].get_attribute("href")
                # Sadece temiz ?p=N URL'leri kabul et, isAjax içerenleri reddet
                if href and "isAjax" not in href:
                    return href
        except:
            pass
        return None

    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        adim = 0
        while True:
            href = sonraki_btn_href()
            if href is None:
                break
            # Elemente tıklamak yerine URL'ye direkt git → StaleElement yok
            driver.get(href)
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            adim += 1
            if adim > 100:
                break

        son = sayfadaki_max_numara()
        print(f"  🔍 Son sayfa: {son} ({adim} adım ilerlendi)")

        # İlk sayfaya geri dön
        driver.get(base_url)
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        return son

    except Exception as ex:
        print(f"  ⚠️  son_sayfa_numarasini_al hatası: {ex}")
        # DÜZELTME: Hata sonrası mutlaka base_url'e dön
        try:
            driver.get(base_url)
            time.sleep(3)
        except:
            pass
        return 1


# ─────────────────────────────────────────────
# Ürün toplama
# ─────────────────────────────────────────────
def urunleri_topla(kategori_adi):
    urunler = driver.find_elements(By.CSS_SELECTOR, "li.product-item")
    sayfa_urunleri = []

    for u in urunler:
        try:
            isim = ""
            for sel in [".product-name", ".product-title", "h2", "h3", "[class*='name']"]:
                try:
                    isim = u.find_element(By.CSS_SELECTOR, sel).text.strip()
                    if isim:
                        break
                except:
                    continue

            fiyat = ""
            for sel in [".price-wrapper .price", ".price", "[class*='price']"]:
                try:
                    fiyat = u.find_element(By.CSS_SELECTOR, sel).text.strip()
                    if fiyat:
                        break
                except:
                    continue

            link = ""
            try:
                link = u.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                pass

            resim = ""
            try:
                resim = u.find_element(By.TAG_NAME, "img").get_attribute("src")
            except:
                pass

            if isim or link:
                sayfa_urunleri.append({
                    "kategori": kategori_adi,
                    "isim": isim,
                    "fiyat": fiyat,
                    "link": link,
                    "resim": resim,
                })
        except:
            continue

    return sayfa_urunleri


# ─────────────────────────────────────────────
# Kategori işleme
# ─────────────────────────────────────────────
def kategori_isle(kategori_url):
    kategori_adi = kategori_url.rstrip("/").split("/")[-1]
    kategori_adi = kategori_adi.replace(".html", "").replace("-", " ").title()
    print(f"\n📂 Kategori: {kategori_adi}")

    base_url = kategori_url.split("?")[0]

    driver.get(base_url)
    time.sleep(3)
    overlay_kaldir()
    scroll_to_bottom()

    # base_url'i parametre olarak geçiyoruz — hata sonrası doğru yere döner
    son_sayfa = son_sayfa_numarasini_al(base_url)
    print(f"  📊 Toplam sayfa: {son_sayfa}")

    kategori_linkleri = set()

    if son_sayfa > 1:
        # Sayı bazlı sayfalama
        for sayfa_no in range(1, son_sayfa + 1):
            if sayfa_no == 1:
                sayfa_url = base_url
            else:
                sayfa_url = f"{base_url}?p={sayfa_no}"
                driver.get(sayfa_url)
                time.sleep(3)
                overlay_kaldir()
                scroll_to_bottom()

            print(f"  📄 Sayfa {sayfa_no}/{son_sayfa}: {sayfa_url}", end=" → ")
            bulunanlar = urunleri_topla(kategori_adi)

            mevcut_linkler = {u["link"] for u in tum_urunler}
            yeni = [u for u in bulunanlar if u["link"] not in mevcut_linkler and u["link"] not in kategori_linkleri]
            for u in yeni:
                kategori_linkleri.add(u["link"])
            tum_urunler.extend(yeni)

            print(f"{len(bulunanlar)} ürün, {len(yeni)} yeni | Toplam: {len(tum_urunler)}")

    else:
        # Fallback: "Sonraki" butonu ile ilerle
        sayfa_no = 1
        print(f"  📄 Sayfa {sayfa_no} (next-buton modu): {base_url}", end=" → ")
        bulunanlar = urunleri_topla(kategori_adi)
        mevcut_linkler = {u["link"] for u in tum_urunler}
        yeni = [u for u in bulunanlar if u["link"] not in mevcut_linkler]
        for u in yeni:
            kategori_linkleri.add(u["link"])
        tum_urunler.extend(yeni)
        print(f"{len(bulunanlar)} ürün, {len(yeni)} yeni | Toplam: {len(tum_urunler)}")

        while True:
            overlay_kaldir()
            # DÜZELTME: Her döngüde elementi yeniden bul, href al, direkt git
            try:
                btns = driver.find_elements(By.CSS_SELECTOR, ".pages-items .item.pages-item-next a")
                if not btns:
                    break
                sonraki_url = btns[0].get_attribute("href")
                # isAjax içeren URL'leri atla
                if not sonraki_url or "isAjax" in sonraki_url:
                    print(f"  ⚠️  Geçersiz next URL: {sonraki_url}, durduruluyor.")
                    break
            except:
                break

            sayfa_no += 1
            driver.get(sonraki_url)
            time.sleep(3)
            overlay_kaldir()
            scroll_to_bottom()

            print(f"  📄 Sayfa {sayfa_no} (next-buton): {sonraki_url}", end=" → ")
            bulunanlar = urunleri_topla(kategori_adi)
            mevcut_linkler = {u["link"] for u in tum_urunler}
            yeni = [u for u in bulunanlar if u["link"] not in mevcut_linkler and u["link"] not in kategori_linkleri]
            for u in yeni:
                kategori_linkleri.add(u["link"])
            tum_urunler.extend(yeni)
            print(f"{len(bulunanlar)} ürün, {len(yeni)} yeni | Toplam: {len(tum_urunler)}")

            if sayfa_no > 200:
                print("  ⚠️  200 sayfa limitine ulaşıldı.")
                break


# ─────────────────────────────────────────────
# Ana akış
# ─────────────────────────────────────────────
try:
    konum_sec()

    for kategori_url in KATEGORILER:
        kategori_isle(kategori_url)

    if not os.path.exists('data'):
        os.makedirs('data')

    tarih = datetime.now().strftime("%Y-%m-%d")
    dosya_adi = f"data/arden_urunler_{tarih}.csv"

    with open(dosya_adi, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["kategori", "isim", "fiyat", "link", "resim"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(tum_urunler)

    print(f"\n{'='*50}")
    print(f"🎉 TOPLAM ÜRÜN: {len(tum_urunler)}")
    print(f"💾 {dosya_adi} kaydedildi")
    print(f"{'='*50}")

finally:
    driver.quit()
