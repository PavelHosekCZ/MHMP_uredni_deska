import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import urllib.request 
import datetime
from unidecode import  unidecode
from urllib.parse import unquote


def scrape():
    # Načtení data posledního stahování
    try:
        f = open("last_run.txt", "r")
        minule = f.read()
        f.close()    
        minule_datum = datetime.datetime.strptime(minule, "%Y-%m-%d")
    except FileNotFoundError:
        now = datetime.datetime.now()
        minule_datum = now - datetime.timedelta(days=14)

    # Start webdriveru, načtení úvodní stránky
    driver = webdriver.Chrome()
    driver.get("https://eud.praha.eu/pub/deska/6000004/4?vizual=mhmp_res&pocet=1000&trideni=oblast&odbor_id_zdroj=&nazev=&cislo_jednaci=&kategorie_id=&oblast_id=57&datum_od=&datum_do=")
        # poznámka: natvrdo zadáno 1000 záznamů. V době psaní kódu se na webu vyfiltrovalo 209 odpovídajících položek od počátku věků, takže by to mělo stačit.

    # Cyklus pro získání všech dat jednotlivých záznamů
    main_div = driver.find_element(By.XPATH, '//*[@id="content"]')
    items = main_div.find_elements(By.XPATH, './/h5') 
    zaznamy = []
    for item in items:
        link = item.find_element(By.TAG_NAME, 'a') 
        zaznamy.append({'nazev': item.text, 'odkaz': link.get_attribute('href')})

    # Vytvoření složky Download, pokud neexistuje
    folder_path = "Download"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)    

    # Otvírání jednotlivých stránek, stahování obsahu
    for item in zaznamy:
        driver.get(item['odkaz'])
        vyveseno = driver.find_element(By.XPATH , '/html/body/div/div/div[1]/div[2]/table/tbody/tr[4]/td').text
        vyveseno_datum = datetime.datetime.strptime(vyveseno, "%d.%m.%Y")
        vyveseno = vyveseno_datum.strftime("%Y-%m-%d")

        if vyveseno_datum < minule_datum:
            break

        main_div = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div[2]')
        links = main_div.find_elements(By.XPATH, './/a') 
        for link in links:
            url = link.get_attribute('href')            
            nazev_zkraceny = (item['nazev'][:50] + '..') if len(item['nazev']) > 50 else item['nazev']
            target = "Download\\" + vyveseno + "   [" + unidecode(unquote(nazev_zkraceny)) + "]   " + unidecode(unquote(url.split('/')[-1]))
            target = target.translate({ord(i):None for i in '"!@#$/:'})
            print("downloading: " + target)
            urllib.request.urlretrieve(url, target)
       
    # Ukončení
    driver.quit()

    print()
    print("Dokončeno prohledávání webu")

    f = open("last_run.txt", "w")
    f.write(datetime.date.today().strftime("%Y-%m-%d"))
    f.close()

if __name__ == "__main__":
    scrape()
