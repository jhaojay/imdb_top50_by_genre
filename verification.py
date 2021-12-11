import csv
import chardet
from os.path import exists
import sys


class verification:
    def __init__(self, file_path):
        """check whether it's a csv file"""
        if file_path.lower().endswith(".csv"):
            self.file = file_path
        else:
            print("Please supply a csv file")

    def check_not_empty(self):
        """return true if file exists and is not empty"""
        file_exists = exists(self.file)
        if file_exists:
            with open(self.file, newline='') as csv_file:
                reader = csv.DictReader(csv_file)
                csv_dict = [row for row in reader]
                if len(csv_dict):
                    return True
        print("File doesn't exist or is empty")
        return False

    def check_utf8(self):
        """return true is the file is likely to be UTF8 encoded"""
        with open(self.file, 'rb') as rawdata:
            # open in raw binary format
            result = chardet.detect(rawdata.read())
            if result["encoding"] == "utf-8":
                return True
            else:
                print("file is not utf-8 encoded")
                return False

    def check_header(self, headers_to_check):
        """supply headers_to_check in list format
        return true if the headers are complete"""
        with open(self.file, newline='') as csv_file:
            reader = csv.reader(csv_file)
            csv_headers = sorted(next(reader))  # using next() to get headers
            if csv_headers == sorted(headers_to_check):
                return True
            else:
                print("Headers don't match.")
                return False

    def check_num_rows(self, target_num):
        """return true if the number of rows match target_num,
        not counting the row of headers"""
        with open(self.file, newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            csv_dict = [row for row in reader]
            if len(csv_dict) == target_num:
                return True
            else:
                print("The number of rows doesn't match.")
                return False


if __name__ == "__main__":
    file = sys.argv[1]
    h = ['cast', 'imdb_movie_id', 'title', 'release_year', 'certificate', 'run_time_min', 'imdb_rating', 'metascore', 'description', 'num_voted_users', 'gross', 'genre', 'ranked_genre', 'ranking_by_genre', 'director']
    if (verification(file).check_not_empty() and
            verification(file).check_utf8() and
            verification(file).check_header(h) and
            verification(file).check_num_rows(1200)):
        print("All criteria satisfied")
