#
# file: entertainment_center.py
# author: lyn evans
# date: 04.29.15
#
import media
import favorite_movies


""" Instantiate Movies to be rendered on the web page """
LongestDay = media.Movie("The Longest Day", "A movie based on the novel written by Cornelius Ryan about D-Day amd the Normandy landings on une 6, 1944, duirng WWII",
                         "http://upload.wikimedia.org/wikipedia/en/7/79/Original_movie_poster_for_the_film_The_Longest_Day.jpg", 
                         "https://www.youtube.com/watch?v=RW5t1V4xm3M", 178, "G", 1962)


JoyeuxNoel = media.Movie("Joyeux Noel", "A French film about the WWI Christmas truce in December 1914",
                         "http://upload.wikimedia.org/wikipedia/en/thumb/d/d8/MerryChristmasfilmPoster3.jpg/220px-MerryChristmasfilmPoster3.jpg",
                         "https://www.youtube.com/watch?v=KRrr-CDXijs", 116, "PG-13", 2005)

Tootsie = media.Movie("Tootsie", "Comedy of a talented actor that adopts the identity of a woman to land an acting job.",
                      "http://upload.wikimedia.org/wikipedia/en/thumb/a/a2/Tootsie_imp.jpg/220px-Tootsie_imp.jpg",
                      "https://www.youtube.com/watch?v=FlXE1Yq0AnQ", 116, "PG", 1982)

Unbroken = media.Movie("Unbroken", "Biographical war drama based o Louie Samperini's survival during WWII",
                       "http://upload.wikimedia.org/wikipedia/en/thumb/7/76/Unbroken_poster.jpg/220px-Unbroken_poster.jpg",
                       "https://www.youtube.com/watch?v=XrjJbl7kRrI", 137, "PG-13", 2014)

MoonriseKingdom = media.Movie("Moonrise Kingdom", "Eccentric love story of two teenagers",
                              "http://upload.wikimedia.org/wikipedia/en/thumb/4/4f/Moonrise_Kingdom_FilmPoster.jpeg/220px-Moonrise_Kingdom_FilmPoster.jpeg",
                              "https://www.youtube.com/watch?v=7N8wkVA4_8s", 94, "PG-13", 2012)

MidnightInParis = media.Movie("Midnight in Paris", "Going back in time to meet authors and painters",
                              "http://upload.wikimedia.org/wikipedia/en/thumb/9/9f/Midnight_in_Paris_Poster.jpg/215px-Midnight_in_Paris_Poster.jpg",
                              "https://www.youtube.com/watch?v=FAfR8omt-CY", 94, "PG-13", 2011)

HungerGames = media.Movie("Hunger Games", "A futuristic reality show revealing human victory in an autocratic society",
                          "http://upload.wikimedia.org/wikipedia/en/thumb/a/ab/Hunger_games.jpg/220px-Hunger_games.jpg",
                          "https://www.youtube.com/watch?v=mfmrPu43DF8", 142, "PG-13", 2012)

MockingJayPart1 = media.Movie("Mockingjay Part 1", "Science fiction war adventure following Katniss Everdeen's survival",
                              "http://upload.wikimedia.org/wikipedia/en/thumb/6/63/MockingjayPart1Poster3.jpg/220px-MockingjayPart1Poster3.jpg",
                              "https://www.youtube.com/watch?v=3PkkHsuMrho", 123, "PG-13", 2014)

MockingJayPart2 = media.Movie("Mockingjay Part 2", "Science fiction war adventure following Katniss Everdeen's victory",
                              "http://upload.wikimedia.org/wikipedia/en/thumb/9/9d/Mockingjay_Part_2_Poster.jpg/220px-Mockingjay_Part_2_Poster.jpg",
                              "https://www.youtube.com/watch?v=4GbcIhjaOxY", 0, "", 2015)

TheForceAwakens = media.Movie("Str Wars: Episode VII - The Force Awakens", "The continuation of Star Wars set 30 years after Return of the Jedi",
                           "http://ia.media-imdb.com/images/M/MV5BMTUwMjU0MzQwNV5BMl5BanBnXkFtZTgwNzQwODUzNTE@._V1_SX214_AL_.jpg",
                           "https://www.youtube.com/watch?v=wCc2v7izk8w", 0, "", 2015)


""" Build movie collection as a list """
moviesList = [LongestDay, JoyeuxNoel, Tootsie, Unbroken, MoonriseKingdom, MidnightInParis, HungerGames, MockingJayPart1, MockingJayPart2, TheForceAwakens]

""" Launch web page """
favorite_movies.open_movies_page(moviesList)

