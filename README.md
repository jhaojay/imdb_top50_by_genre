# Introduction
In this case study, two ETL pipelines were developed. One is that scrapes the top 50 movies from the list of "Top Rated English Movies by Genre" of each genre into a local csv file.The second ETL pipeline is that extracts raw data from the csv file, performs necessary transformations and loads into postgresSQL database.
<br/><br/>
Movies' imdb ids, titles, release years, certificates, running time, ratings, metascores, descriptions, votes, gross, rankings by genre, directors and casts are scrapped and stored.

# Database schema design
(click to enlarge):
![alt text](https://github.com/jhaojay/imdb_top50_by_genre/blob/main/charts/ERD.JPG?raw=true)

# Code design flowchats
![alt text](https://github.com/jhaojay/imdb_top50_by_genre/blob/main/charts/flowchart1.JPG?raw=true)
<br/><br/>
![alt text](https://github.com/jhaojay/imdb_top50_by_genre/blob/main/charts/flowchart2.JPG?raw=true)

# Dependencies
Python 3.8.12 and the following Python libraries were used:
```python
# to open and load data into csv files
csv
```
```python
# to scrape and parse movie information from IMDB
beautifulsoup4, requests, re, lxml 
```
```python
# to configure and connect PostgreSQL
psycopg2, configparser 
```
```python
# to verify .csv file
chardet, os, sys
```
# Installation
Installing the necessary dependencies listed in the Dependencies section:
```
$pip install -r requirements.txt
```

# Usage
First, scrape all the target movie information from IMDB and save it to "movie_output.csv":
```python
$python imdb_scrapper_to_csv.py
```
<br/><br/>
Then, supply credentials in the database.ini file.

<br/><br/>
Lastly, load all the rows from the output csv file into postgresSQL database:
```python
$python load_csv_to_db.py
```

# Validation
verification.py checks the output csv file for the following criteria:
1. File is in .csv format.
2. File exists and not empty.
3. File is utf-8 encoded.
4. File has complete hearders.
5. File contains the correct number of row.

```python
$python verification.py movie_output.csv
```
