import csv
from mydb import MyDB


class IMDBLoader:
    def __init__(self, db, csv_file_path):
        self.db = db
        self.csv_file_path = csv_file_path

        # clear all tables in database during init
        tables = ["movie_info",
                  "genre",
                  "movie_genre",
                  "person",
                  "movie_info",
                  "movie_genre",
                  "movie_ranking_by_genre",
                  "movie_director",
                  "movie_cast"]
        for table in tables:
            sql = f'''DROP TABLE IF EXISTS {table}'''
            self.db.query(sql)

    def load_genre(self):
        create_script = ''' CREATE TABLE IF NOT EXISTS genre (
                            id          int         NOT NULL PRIMARY KEY,
                            genre_type  varchar(20) NOT NULL)'''
        self.db.query(create_script)

        with open(self.csv_file_path, newline='', encoding='utf-8') as cf:
            content = csv.DictReader(cf)
            genres = set()
            for row in content:
                genres.add(row["ranked_genre"].strip())
            insert_script = '''INSERT INTO 
                                genre (id, genre_type) 
                                VALUES (%s, %s)'''
            genre_id = 1
            for genre in genres:
                self.db.query(insert_script, (genre_id, genre))
                genre_id += 1

            insert_script = '''INSERT INTO 
                                genre (id, genre_type) 
                                VALUES (%s, %s)'''
            self.db.query(insert_script, (genre_id, "News"))
            print("genre table loaded")

    def load_person(self):
        # create person table and load data from csv
        create_script = ''' CREATE TABLE IF NOT EXISTS person (
                                id              INT          NOT NULL,
                                imdb_person_id  VARCHAR(10)  NOT NULL  PRIMARY KEY,
                                full_name       VARCHAR(30)  NOT NULL)'''
        self.db.query(create_script)
        with open(self.csv_file_path, newline='', encoding='utf-8') as cf:
            content = csv.DictReader(cf)
            person_id = 1
            for row in content:
                # concatenate directors and casts
                people = row["director"].split(',') + row["cast"].split(',')
                for person in people:

                    # in rare occasion cast info is not provided
                    if "NULL" not in person:
                        full_name, imdb_person_id = person.split('@')
                        insert_script = '''INSERT INTO
                                            person (id, imdb_person_id, full_name)
                                            VALUES (%s, %s, %s)
                                            ON CONFLICT DO NOTHING '''
                        self.db.query(insert_script, (person_id, imdb_person_id, full_name))

                        # increases id only when person is unique
                        if self.db.status_message()[-1] == '1':
                            person_id += 1
                    else:
                        insert_script = '''INSERT INTO
                                            person (id, imdb_person_id, full_name)
                                            VALUES (%s, %s, %s)
                                            ON CONFLICT DO NOTHING '''
                        self.db.query(insert_script, (-1, "NULL", "NULL"))
        print("person table loaded")

    def load_movie_info(self):
        # create movie_info table and load data from csv
        create_script = ''' CREATE TABLE IF NOT EXISTS movie_info (
                                id               INT           NOT NULL,
                                imdb_movie_id    VARCHAR(10)   NOT NULL PRIMARY KEY,
                                title            VARCHAR(100)  NOT NULL,
                                release_year     CHAR(4)       NOT NULL,
                                certificate      VARCHAR(10)   NOT NULL,
                                run_time_min     INT           NOT NULL,
                                imdb_rating      FLOAT         NOT NULL,
                                metascore        INT           NOT NULL,
                                description      VARCHAR(1000) NOT NULL,
                                num_voted_users  INT           NOT NULL,
                                gross            INT           NOT NULL)'''
        self.db.query(create_script)

        movie_id = 1
        with open(self.csv_file_path, newline='', encoding='utf-8') as cf:
            content = csv.DictReader(cf)

            for row in content:
                insert_script = '''INSERT INTO 
                                    movie_info (id,
                                                imdb_movie_id,
                                                title,
                                                release_year,
                                                certificate,
                                                run_time_min,
                                                imdb_rating,
                                                metascore,
                                                description,
                                                num_voted_users,
                                                gross) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT DO NOTHING'''

                insert_val = (movie_id,
                              row["imdb_movie_id"],
                              row["title"],
                              row["release_year"],
                              row["certificate"],
                              row["run_time_min"],
                              row["imdb_rating"],
                              row["metascore"],
                              row["description"],
                              row["num_voted_users"],
                              row["gross"])
                self.db.query(insert_script, insert_val)

                if self.db.status_message()[-1] == '1':  # increases id only when movie is unique
                    movie_id += 1

        # change primary key from imdb_movie_id to id
        alter_script = "ALTER TABLE movie_info DROP CONSTRAINT movie_info_pkey"
        self.db.query(alter_script)
        alter_script = "ALTER TABLE movie_info ADD PRIMARY KEY (id)"
        self.db.query(alter_script)

        print("movie_info table loaded")

    def load_movie_genre(self):
        # create movie_genre table and load data from csv
        create_script = ''' CREATE TABLE IF NOT EXISTS movie_genre (
                                movie_id  INT NOT NULL,
                                genre_id  INT NOT NULL,
                                PRIMARY KEY (movie_id, genre_id))'''
        self.db.query(create_script)

        with open(self.csv_file_path, newline='', encoding='utf-8') as cf:
            content = csv.DictReader(cf)

            for row in content:
                genres_for_each_movie = row["genre"].split(',')
                for genre in genres_for_each_movie:
                    # fetch genre.id
                    fetch_script = '''SELECT id FROM genre WHERE genre_type=%s '''
                    genre_id_fetched = self.db.query(fetch_script, (genre.strip(),), fetch=True)

                    genre_id = genre_id_fetched[0][0]

                    # fetch movie_info.id
                    fetch_script = '''SELECT id FROM movie_info WHERE imdb_movie_id=%s '''
                    movie_id_fetched = self.db.query(fetch_script, (row["imdb_movie_id"],), fetch=True)
                    movie_id = movie_id_fetched[0][0]
                    # insert data into movie_genre table
                    insert_script = '''INSERT INTO 
                                        movie_genre (movie_id, genre_id) 
                                        VALUES (%s, %s)
                                        ON CONFLICT DO NOTHING'''
                    self.db.query(insert_script, (movie_id, genre_id))

        print("movie_genre table loaded")

    def load_movie_ranking_by_genre(self):
        # create movie_ranking_by_genre table and load data from csv
        create_script = ''' CREATE TABLE IF NOT EXISTS movie_ranking_by_genre (
                                movie_id        INT NOT NULL,
                                ranked_genre_id INT NOT NULL,
                                ranking         INT NOT NULL,
                                PRIMARY KEY (movie_id, ranked_genre_id))'''
        self.db.query(create_script)
        with open(self.csv_file_path, newline='', encoding='utf-8') as cf:
            content = csv.DictReader(cf)

            for row in content:
                # fetch movie_info.id
                fetch_script = '''SELECT id FROM movie_info WHERE imdb_movie_id=%s '''
                movie_id_fetched = self.db.query(fetch_script, (row["imdb_movie_id"],), fetch=True)
                movie_id = movie_id_fetched[0][0]

                # fetch genre.id
                fetch_script = '''SELECT id FROM genre WHERE genre_type=%s '''
                genre_id_fetched = self.db.query(fetch_script, (row["ranked_genre"].strip(),), fetch=True)
                ranked_genre_id = genre_id_fetched[0][0]

                # insert data into movie_genre table
                insert_script = '''INSERT INTO 
                                    movie_ranking_by_genre (movie_id, ranked_genre_id, ranking) 
                                    VALUES (%s, %s, %s)
                                    ON CONFLICT DO NOTHING'''
                self.db.query(insert_script, (movie_id, ranked_genre_id, row["ranking_by_genre"]))

        print("movie_ranking_by_genre table loaded")

    def load_movie_director(self):
        # create movie_director table and load data from csv
        create_script = ''' CREATE TABLE IF NOT EXISTS movie_director (
                                movie_id   INT  NOT NULL,
                                person_id  INT  NOT NULL,
                                PRIMARY KEY (movie_id, person_id))'''
        self.db.query(create_script)
        with open(self.csv_file_path, newline='', encoding='utf-8') as cf:
            content = csv.DictReader(cf)
            for row in content:
                # fetch movie_id
                fetch_script = '''SELECT id FROM movie_info WHERE imdb_movie_id=%s '''
                movie_id_fetched = self.db.query(fetch_script, (row["imdb_movie_id"],), fetch=True)
                movie_id = movie_id_fetched[0][0]
                for dirct in row["director"].split(','):
                    full_name, imdb_person_id = dirct.split('@')

                    # fetch person_id
                    fetch_script = '''SELECT id FROM person WHERE imdb_person_id=%s '''
                    person_id_fetched = self.db.query(fetch_script, (imdb_person_id,), fetch=True)
                    person_id = person_id_fetched[0][0]

                    # insert movie_id and person_id to table:movie_director
                    insert_script = '''INSERT INTO
                                        movie_director (movie_id, person_id)
                                        VALUES (%s, %s)
                                        ON CONFLICT DO NOTHING '''
                    self.db.query(insert_script, (movie_id, person_id))

        print("movie_director table loaded")

    def load_movie_cast(self):
        # create movie_cast table and load data from csv
        create_script = ''' CREATE TABLE IF NOT EXISTS movie_cast (
                                movie_id   INT  NOT NULL,
                                person_id  INT  NOT NULL,
                                PRIMARY KEY (movie_id, person_id))'''
        self.db.query(create_script)
        with open(self.csv_file_path, newline='', encoding='utf-8') as cf:
            content = csv.DictReader(cf)
            for row in content:
                # fetch movie_id
                fetch_script = '''SELECT id FROM movie_info WHERE imdb_movie_id=%s '''
                movie_id_fetched = self.db.query(fetch_script, (row["imdb_movie_id"],), fetch=True)
                movie_id = movie_id_fetched[0][0]
                for cast in row["cast"].split(','):
                    if "NULL" not in cast:
                        full_name, imdb_person_id = cast.split('@')

                        # fetch person_id
                        fetch_script = '''SELECT id FROM person WHERE imdb_person_id=%s '''
                        person_id_fetched = self.db.query(fetch_script, (imdb_person_id,), fetch=True)
                        person_id = person_id_fetched[0][0]

                        # insert movie_id and person_id to table:movie_director
                        insert_script = '''INSERT INTO
                                            movie_cast (movie_id, person_id)
                                            VALUES (%s, %s)
                                            ON CONFLICT DO NOTHING '''
                        self.db.query(insert_script, (movie_id, person_id))
                    else:
                        insert_script = '''INSERT INTO
                                            movie_cast (movie_id, person_id)
                                            VALUES (%s, %s)
                                            ON CONFLICT DO NOTHING '''
                        self.db.query(insert_script, (movie_id, -1))

        print("movie_cast table loaded")


if __name__ == "__main__":
    mydb = MyDB()
    mydb.connect()

    file_path = "movie_output.csv"
    loader = IMDBLoader(mydb, file_path)

    loader.load_genre()
    loader.load_person()
    loader.load_movie_info()

    loader.load_movie_genre()
    loader.load_movie_ranking_by_genre()
    loader.load_movie_director()
    loader.load_movie_cast()

    mydb.close()
