from email.generator import BytesGenerator
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import random
import datetime as dt
import smtplib
import email
from email import policy
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import telebot

bot = telebot.TeleBot("7707835345:AAHsRr45MfCoTu5XoyB3QoUn1v3dTO3giQc")
bot.send_message(6375932552, "Amazon Bot is ready, send a link")

def amazon_bot(link_to_product):
    product_link = link_to_product
    def generate_date(): # generate delivery date
        current_date = dt.date.today()
        monate = ["Januar", "Februar", "März", "April", "Mai", "Juni", # Months for date generation
                  "Juli", "August", "September", "Oktober", "November", "Dezember"]
        order_delay = random.randint(5, 10)
        formatted = f"{current_date.day + order_delay}. {monate[current_date.month - 1]} - {current_date.day + 2 + order_delay}. {monate[current_date.month - 1]}"
        return formatted

    def gen_order_number(): # generate order number
        nr = ""
        for i in range(3):
            nr = nr+str(random.randint(0,9))
        nr = nr+"-"
        for i in range(7):
            nr = nr+str(random.randint(0,9))
        nr = nr + "-"
        for i in range(7):
            nr = nr+str(random.randint(0,9))
        return nr

    geckodriver_path = r"C:\Users\marce\Desktop\amazon_bot\geckodriver.exe"  # Pfad zum Geckodriver
    options = Options()
    options.headless = True
    options.add_argument("--headless")
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"  # Pfad zum Tor-Browser
    options.set_preference("intl.accept_languages", "en-US, en")  
    options.set_preference("dom.webdriver.enabled", False)  
    options.set_preference("useAutomationExtension", False)
    options.set_preference("media.peerconnection.enabled", False)  
    service = Service(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options) 
    time.sleep(5)
    
    try:
        driver.get(link_to_product)
    except:
        print("No link entered")
    time.sleep(5)
    product_name = driver.find_element(By.CSS_SELECTOR, "#productTitle")
    try:
        product_price = driver.find_element(By.CLASS_NAME, "a-price-whole")
    except:
        product_price = driver.find_element(By.CLASS_NAME, "a-price-range")
    try:
        product_price_fraction = driver.find_element(By.CLASS_NAME, "a-price-fraction")
    except:
        product_price_fraction = "00"
    product_image = driver.find_element(By.CSS_SELECTOR, "#landingImage").get_attribute("src")

    einsetze = "SS90"

    replace_start = product_image.find("_AC_SX679_")
    if replace_start != -1:
        replace_end = replace_start + len("_AC_SX679_")
        thumbnail = product_image[:replace_start] + einsetze + product_image[replace_end:]
    else:
        thumbnail = product_image

    # === Pfade ===
    input_path = "placeholder.eml"
    output_path = "filled_order.eml"

    # === Werte als einzelne Variablen ===
    article_name = product_name.text
    price = product_price.text + "," + product_price_fraction.text
    amount = "1"
    order_nr = gen_order_number()
    delivery_date = generate_date()
    wish_adress = "Wisher's Adress"
    seller = "Amazon.com, Inc"

    print(f"""
    Artikelname: {article_name}
    Preis: {price}
    Menge: {amount}
    Bestellnummer: {order_nr}
    Lieferdatum: {delivery_date}
    Wunschadresse: {wish_adress}
    Verkäufer: {seller}
    """)

    # === Platzhalter-Zuordnung zur Variable (Platzhalter -> Variable-Name als String) ===
    placeholder_map = {
        "{{ARTIKELNAME}}": "article_name",
        "{{PREIS}}": "price",
        "{{MENGE}}": "amount",
        "{{BESTELLNUMMER}}": "order_nr",
        "{{LIEFERDATUM}}": "delivery_date",
        "{{WUNSCHADRESSE}}": "wish_adress",
        "{{VERKAEUFER}}": "seller",
        "{{BILD}}": "thumbnail"
    }

    # === E-Mail load ===
    with open(input_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    # === HTML extraction ===
    html = ''
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors="replace")
            break

    # === replace placeholders with values ===
    for key, var_name in placeholder_map.items():
        value = locals().get(var_name, "")  # greift auf die Variable mit dem Namen var_name zu
        html = html.replace(key, value)

    # === HTML conversion ===
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            part.set_payload(html.encode(part.get_content_charset() or "utf-8"))
            break

    # === save new email ===
    with open(output_path, "wb") as f:
        gen = BytesGenerator(f)
        gen.flatten(msg)

    print(f"\n✅ The file with your input was saved as:: {output_path}")

    # load eml email
    with open("filled_order.eml", "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    html_part = None
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_part = part.get_payload(decode=True).decode(part.get_content_charset(), errors='replace')
    if not html_part:
        html_part = "<html><body><h1>Standard HTML Inhalt</h1></body></html>"

    # create email as MIMEMultipart-object
    new_msg = MIMEMultipart("alternative")
    new_msg["From"] = "privat1345@gmail.com"
    new_msg["To"] = "privat1345@gmail.com"
    new_msg["Subject"] = "Your order on Amazon"

    # combine text and html
    text_part = MIMEText("Dies ist eine Textversion der E-Mail.", "plain")
    html_part = MIMEText(html_part, "html")

    # add parts to email
    new_msg.attach(text_part)
    new_msg.attach(html_part)

    # send email
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "privat1345@gmail.com"
    smtp_password = "herhkviscoszbloy"  # App-Passwort verwenden, nicht dein reguläres Passwort.

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(new_msg)  # send email

    print("✅ E-Mail sent successfully")


@bot.message_handler(func=lambda message: True)
def bot_start(message):
    bot.send_message(message.chat.id, "Doing My Thing, please wait")
    amazon_bot(message.text)
    bot.send_message(message.chat.id, "Done")

bot.polling(none_stop=True)
