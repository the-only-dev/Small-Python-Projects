import requests
from bs4 import BeautifulSoup
import csv, os

#CSV file setup
filename = "Quotes.csv"
csv_file = open(filename, "w", newline='', encoding="utf-8")
writer = csv.writer(csv_file)
writer.writerow(["Quote","Author","Tags"]) #for heading

#looping through pages
page = 1
while True:
  url = f"http://quotes.toscrape.com/page/{page}/"
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")

  #find all quote blocks
  quotes = soup.find_all("div", class_="quote")

  if not quotes:
    break

  for quote in quotes:
    text = quote.find("span", class_="text").text
    author = quote.find("small", class_="author").text
    try:
      if(quote.find("a", class_="tag").text):
        tag = quote.find("a", class_="tag").text
    except:
      tag = ""
    writer.writerow([text, author, tag])

  print(f"Scrapped Pages {page}") 
  page += 1
  
csv_file.close()
print(f"\nScraping Complete! Data saved in file '{filename}")
os.startfile(filename)