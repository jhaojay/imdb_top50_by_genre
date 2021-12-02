from bs4 import BeautifulSoup
import requests
import re
import csv

url = "https://www.imdb.com/feature/genre?ref_=fn_asr_ge"
response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

# open the file in the write mode
f = open("movie_output.csv", "w", newline="", encoding="utf-8")
writer = csv.writer(f)
writer.writerow(
    [
        "imdb_movie_id",
        "title",
        "release_year",
        "certificate",
        "run_time_min",
        "imdb_rating",
        "metascore",
        "description",
        "num_voted_users",
        "gross",
        "genre",
        "ranked_genre",
        "ranking_by_genre",
        "director",
        "cast",
    ]
)

target_widget = soup.select("div.aux-content-widget-2")[3]
links = [a.attrs.get("href") for a in target_widget.select("div.table-cell.primary a")]
genres_ranked = [
    a.text.strip().replace(" ", "-")
    for a in target_widget.select("div.table-cell.primary a")
]


for num_link in range(len(links)):
    print(f"Scraping movies in {genres_ranked[num_link]}")
    urls = "https://www.imdb.com" + links[num_link]
    response = requests.get(urls)
    soup = BeautifulSoup(response.text, "lxml")
    movie_info_blocks = soup.select("div.lister-item-content")

    # info that guarantees to exist
    imdb_id_strs = [
        a["href"].split("/")[2] for a in soup.select("h3.lister-item-header a")
    ]
    titles = [a.text for a in soup.select("h3.lister-item-header a")]
    num_voted_users = [
        span["data-value"]
        for span in soup.select("p.sort-num_votes-visible > span:nth-of-type(2)")
    ]
    release_year_raw = [
        y.text for y in soup.select("span.lister-item-year.text-muted.unbold")
    ]
    release_years = [re.findall("[0-9]+", year)[0] for year in release_year_raw]
    certificates = [c.text for c in soup.select("span.certificate")]
    runtime_min = [t.text.split()[0] for t in soup.select("span.runtime")]
    imdb_ratings = [
        float(r.text)
        for r in soup.select("div.inline-block.ratings-imdb-rating strong")
    ]
    genres = [g.text.strip("\n").replace(" ", "") for g in soup.select("span.genre")]
    descriptions = [
        child.find_all("p")[1].text.strip("\n") for child in movie_info_blocks
    ]
    directors_and_casts = [child.find_all("p")[2] for child in movie_info_blocks]
    directors = []
    casts = []
    directors_scrapped = 0

    for dc in directors_and_casts:
        cast_for_each_movie = ""
        directors_for_each_movie = ""
        casts_exist = 0
        for info in dc:

            if "Tag" == type(info).__name__:
                if info.text == "|":
                    directors_scrapped = 1
                    casts_exist = 1
                    continue

                if not directors_scrapped:
                    dir_imdb_id = info["href"].split("/")[2]
                    dir_name = info.text
                    directors_for_each_movie += f"{dir_name}@{dir_imdb_id},"
                else:
                    cast_imdb_id = info["href"].split("/")[2]
                    cast_name = info.text
                    cast_for_each_movie += f"{cast_name}@{cast_imdb_id},"

        if not casts_exist:
            cast_for_each_movie = "NULL"

        casts.append(cast_for_each_movie.strip(","))
        directors_scrapped = 0
        directors.append(directors_for_each_movie.strip(","))

    # scrap certificates, metascores and grosses, which are not guaranteed to exist
    grosses = []
    metascores = []
    certificates = []

    for mb in movie_info_blocks:
        certificate_results = mb.select("span.certificate")
        if certificate_results:
            certificates.append(certificate_results[0].text)
        else:
            certificates.append("NULL")  # NULL means certificate is not provided

        metascore_results = mb.select("div.inline-block.ratings-metascore")
        if metascore_results:
            ms = metascore_results[0].select("span.metascore")[0].text.strip()
            metascores.append(ms)
        else:
            metascores.append(-1)  # -1 means the metascore is not provided

        votes_gross_bar = mb.select("p.sort-num_votes-visible")
        for vg_raw in votes_gross_bar:
            vg = vg_raw.find_all("span", {"name": "nv"})
            if len(vg) > 1:
                grosses.append(vg[1]["data-value"].replace(",", ""))
            else:
                grosses.append(-1)  # -1 means the gross is not provided

    for i in range(len(titles)):
        writer.writerow(
            [
                imdb_id_strs[i],
                titles[i],
                release_years[i],
                certificates[i],
                runtime_min[i],
                imdb_ratings[i],
                metascores[i],
                descriptions[i],
                num_voted_users[i],
                grosses[i],
                genres[i],
                genres_ranked[num_link],
                i + 1,
                directors[i],
                casts[i],
                ]
        )
    print("Done\n")
f.close()

print("Finished")
