from bs4 import BeautifulSoup
import csv, requests

try: 
  #Try Creating File
  filename = "CheatSheetNew.csv"
  csv_file = open(filename, "w", newline='', encoding="utf-8")
  writer = csv.writer(csv_file)
  writer.writerow(["Number","Category", "Tags" ,"Links"])

  #Try Requesting webpage
  url = "https://dev.to/devmount/a-cheatsheet-of-128-cheatsheets-for-developers-f4m?ref=dailydev"
  try:
    response = requests.get(url)
    response.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(f"Request Error : {e}")
    csv_file.close()
    exit()

  soup = BeautifulSoup(response.text, "html.parser")

  #Scraping Logic
  num = 1
  titles = soup.find_all("h3")
  for title in titles:
    mainTitle = title.text.strip()
    nextTags = title.find_next_siblings()

    for nextTag in nextTags:
      if nextTag.name == "h3":
        break

      if nextTag.name == "h4":
        category = nextTag.text.strip()
        pTag = nextTag.find_next_sibling("p")

        if pTag:
          links = pTag.find_all("a")

          for link in links:
            linkText = link.text.strip()
            writer.writerow([num, mainTitle, category, linkText])
            num += 1

  csv_file.close()
  print(f"Got All Links Successfully")
except:
  print("Some Error Occured")