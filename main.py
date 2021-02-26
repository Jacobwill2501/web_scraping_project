import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# Setting panda data frame settings
pd.set_option('display.width', 2000)
pd.set_option('display.max_columns', 7)

# getting english translated titles
headers = {"Accept-Language": "en-US,en;q=0.5"}

# request the contents of the url
url = "https://www.imdb.com/search/title/?groups=top_1000&ref_=adv_prv"
results = requests.get(url, headers=headers)

# Using beautifulsoup
soup = BeautifulSoup(results.text, "html.parser")

# initializing empty lists where data will be stored
titles = []
years = []
time = []
imdb_ratings = []
metascores = []
votes = []
us_gross = []

# store all divs to variable, tells scraper to find all of the 'lister-item mode-advanced' divs
movie_div = soup.find_all('div', class_='lister-item mode-advanced')

# initiating the loop that will go through each div/movie
for container in movie_div:
    # Name of the movie
    name = container.h3.a.text
    titles.append(name)

    # Year the movie was released
    year = container.h3.find('span', class_='lister-item-year').text
    years.append(year)

    # Runtime of the movie
    # runtime = container.p.find('span', class_='runtime').text if container.p.find('span', class_='runtime') else '-'
    if container.p.find('span', class_='runtime'):
        runtime = container.p.find('span', class_='runtime').text
    else:
        runtime = False
    time.append(runtime)

    # IMDB rating of the movie
    imdb = float(container.strong.text)
    imdb_ratings.append(imdb)

    # Metascore of the movie
    if container.find('span', class_='metascore'):
        m_score = container.find('span', class_='metascore').text
    else:
        m_score = False
    metascores.append(m_score)

    # New variable because next two values are in same named classes
    nv = container.find_all('span', attrs={'name': 'nv'})

    # Number of votes
    vote = nv[0].text
    votes.append(vote)

    # Gross earnings of movie
    if len(nv) > 1:
        grosses = nv[1].text
    else:
        grosses = '-'
    us_gross.append(grosses)

movies = pd.DataFrame({
    'movie': titles,
    'year': years,
    'timeMin': time,
    'imdb': imdb_ratings,
    'metascore': metascores,
    'votes': votes,
    'us_grossMillions': us_gross,
})

# Cleaning year column, string to int
movies['year'] = movies['year'].str.extract('(\d+)').astype(int)

# Cleaning time column, string to int
movies['timeMin'] = movies['timeMin'].str.extract('(\d+)').astype(int)

# Cleaning metascore column, string to int
movies['metascore'] = movies['metascore'].astype(int)

# Cleaning votes column, string to int
movies['votes'] = movies['votes'].str.replace(',', '').astype(int)

# Cleaning gross millions column, string to float
movies['us_grossMillions'] = movies['us_grossMillions'].map(lambda x: x.lstrip('$').rstrip('M'))
movies['us_grossMillions'] = pd.to_numeric(movies['us_grossMillions'], errors='coerce')

print(movies)
print(movies.dtypes)
movies.to_csv('movies.csv')
