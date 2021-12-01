# Introduction



# Dependencies
This project requires Python 3.8.12 and the following Python libraries:
```python
#to open and load data into csv files
csv
```
```python
#to scrape and parse movie infomation from IMDB
beautifulsoup4, requests, re, lxml 
```
```python
#to configer and connect PostgreSQL
psycopg2, configparser 
```

# Installation
Installing the necessary dependencies listed in the Dependencies section:
```
pip install -r requirements.txt
```

# Usage
First, scrape all the target movie infomation from IMDB and save it to "movie_output.csv":
```python
python imdb_scrapper_to_csv.py
```
Then, load all the rows from the output csv file into postgresSQL database:
```python
python load_csv_to_sql.py
```

# Validation
First, check the total row count of the output csv file in Python console.
it should contain 1201 rows including a row of headers:
```python
>>> import csv
>>> csv_file = "movie_output.csv"
>>> with open(csv_file,"r") as f:
...     reader = csv.reader(f,delimiter = ",")
...     print(len(list(reader)))

1201
```
<br/><br/>
Next, check the total row count in the "movie_ranking_by_genre" table in pgAdmin4:
```SQL
SELECT COUNT(*)
FROM movie_ranking_by_genre
```
| count | 
| :---: |
| 1200 |

<br/><br/>
Lastly, randomly select 10 rows from the database as an sample to validate the infomation:
```SQL
SELECT *
FROM
	(SELECT MOVIE_INFO.TITLE,
	 		MOVIE_INFO.IMDB_RATING,	 
			GENRE.GENRE_TYPE,
			MOVIE_RANKING_BY_GENRE.RANKING
		FROM MOVIE_INFO
		JOIN MOVIE_RANKING_BY_GENRE ON MOVIE_RANKING_BY_GENRE.MOVIE_ID = MOVIE_INFO.ID
		JOIN GENRE ON GENRE.ID = MOVIE_RANKING_BY_GENRE.RANKED_GENRE_ID) AS INFO
ORDER BY RANDOM()
LIMIT 10
```
