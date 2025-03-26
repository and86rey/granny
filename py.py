import requests
from bs4 import BeautifulSoup
import numpy as np
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Step 1: Scrape Berlin Lotto past results
def fetch_lotto_results():
    url = "https://www.lotto-berlin.de/gewinnzahlen?gbn=7"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    numbers = []
    for row in soup.find_all("div", class_="winning-numbers"):  # Update selector as needed
        nums = [int(n.text) for n in row.find_all("span", class_="number")]
        if nums:
            numbers.append(nums)
    
    return numbers

# Step 2: Store results in SQLite database
def store_results(numbers):
    conn = sqlite3.connect("lotto_results.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num1 INTEGER, num2 INTEGER, num3 INTEGER,
            num4 INTEGER, num5 INTEGER, num6 INTEGER
        )
    """)
    
    for nums in numbers:
        cursor.execute("INSERT INTO results (num1, num2, num3, num4, num5, num6) VALUES (?, ?, ?, ?, ?, ?)", tuple(nums))
    
    conn.commit()
    conn.close()

# Step 3: Analyze & Predict Most Common Numbers
def analyze_results():
    conn = sqlite3.connect("lotto_results.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM results")
    all_numbers = np.array(cursor.fetchall()).flatten()
    
    unique, counts = np.unique(all_numbers, return_counts=True)
    freq_numbers = unique[np.argsort(-counts)][:6]  # Get top 6 most common numbers
    
    conn.close()
    return freq_numbers

# Step 4: Send Email Notification
def send_email(numbers_to_avoid):
    sender_email = "zaharov.a.a.it@gmail.com"
    receiver_email = "zaharov.a.a.it@gmail.com"
    password = "$brfrum0XXXit"
    
    subject = "Lotto Berlin - Numbers to Avoid This Week"
    body = f"Based on analysis, the most probable winning numbers are: {numbers_to_avoid}. Avoid these!"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# Run all steps
def main():
    lotto_numbers = fetch_lotto_results()
    store_results(lotto_numbers)
    numbers_to_avoid = analyze_results()
    send_email(numbers_to_avoid)

if __name__ == "__main__":
    main()
