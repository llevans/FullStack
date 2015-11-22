#
# file: media.py
# author: lyn evans
# date: 04.29.15
#
import webbrowser

class Video():
    """ This class is the base class to define videos, either movies, tv shows, or shorter videos uploaded to the internet """
    def __init__(self, title, duration):
       self.title = title
       self.duration = duration

class Movie(Video):
    """ This class provides a way to store movie related information """
    VALID_RATINGS = ["G", "PG", "PG-13", "R"]

    def __init__(self, movie_title, movie_storyline, poster_image, trailer_youtube, duration, rating, year_released):
        Video.__init__(self, movie_title, duration)
        self.movie_storyline= movie_storyline
        self.poster_image_url = poster_image
        self.trailer_youtube_url = trailer_youtube
        """ Validate the movie rating """
        if rating in self.VALID_RATINGS:
            self.rating = rating
        else:
            self.rating = "Not Yet Rated"
        self.year_released = year_released

    def show_trailer(self):
        """ Launch the video trailer viewer """
        webbrowser.open(self.trailer_youtube_url)
