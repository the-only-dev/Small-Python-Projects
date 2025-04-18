import requests, csv, os
from bs4 import BeautifulSoup

#Create CSV file
filename = "Laptops.csv"
csv_file = open(filename, "w",newline='',encoding="utf-8")
writer = csv.writer(csv_file)
writer.writerow(["Product Name","Price","Description"])

#Scrape Website
url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

products = soup.find_all("div", class_="thumbnail")

for product in products:
  name = product.find("a", class_="title").text.strip()
  price = product.find("span", itemprop="price").text.strip()
  desc = product.find("p", class_="description").text
  writer.writerow([name, price, desc])

csv_file.close()
print(f"Scraping Complete")
os.startfile(filename)