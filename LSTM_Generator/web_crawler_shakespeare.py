import bs4 as bs
import urllib.request
import os
import csv

"""Script used to collect all of Shakespeare's works in one file."""

main_sauce = urllib.request.urlopen("http://shakespeare.mit.edu/index.html").read()
main_page = "http://shakespeare.mit.edu/%s"
main_soup = bs.BeautifulSoup(main_sauce, 'lxml')  # source, parser

# print(soup.find_all('a'))
# for quote in soup.find_all('a'):
#     print(quote.text)
# print(soup.get_text())
pass

plays = []        # get urls of every play
for link in main_soup.find_all('a')[2:-7]:
    plays.append(main_page % (link.get('href').replace('index', 'full')))

with open(os.path.join('./datasets', "shakespeare.csv"), mode="w") as f:  # write to csv
    writer = csv.writer(f, delimiter=',')
    for play in plays[:38]:  # every play
        play_src = urllib.request.urlopen(play).read()
        soup = bs.BeautifulSoup(play_src, 'lxml')
        title = soup.title.text.split(":")[0].replace(',', "$")
        text = soup.get_text().replace(',', "$")  # turn every , into a $ to avoid messing up CSV format
        row = [title, text]
        writer.writerow(row)

