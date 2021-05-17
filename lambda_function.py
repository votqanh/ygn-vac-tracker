import email
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import config


def send_email(body):
    SENDER = config.sender
    SENDERNAME = config.name
    RECIPIENT = config.recipient
    USERNAME_SMTP = config.aws_key
    PASSWORD_SMTP = config.aws_secret
    HOST = "email-smtp.us-east-2.amazonaws.com"
    PORT = 587

    SUBJECT = 'VAC Status Update'
    BODY_TEXT = body

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg['To'] = RECIPIENT

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(BODY_TEXT, 'plain')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)

    # Try to send the message.
    try:
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        # stmplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())
        server.close()

    # Display an error message if something goes wrong.
    except Exception as e:
        print("Error: ", e)
    else:
        print("Email sent!")


def lambda_handler(event, context):
    url = 'https://visa.vfsglobal.com/mmr/en/can/news/covid-update'

    ssl._create_default_https_context = ssl._create_unverified_context

    options = Options()
    options.headless = True
    fp = webdriver.FirefoxProfile()
    path = 'geckodriver'

    status_xpath = '/html/body/div[1]/div/div/main/div/div/div[2]/div/p'

    with webdriver.Firefox(executable_path=path, firefox_profile=fp, options=options) as driver:
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, status_xpath)))
        status = driver.find_element_by_xpath(status_xpath).text

    prev_status = 'The Canada Visa Application Centre in Yangon will remain closed until further notice due to the ' \
                  'Covid-19. Please visit this website for further updates. '

    if status == prev_status:
        send_email(status)
    else:
        print('No update')
