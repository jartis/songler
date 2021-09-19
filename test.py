import unittest
from yt import getYTArtistTitle


class Test_getYTArtistTitle(unittest.TestCase):
    def test_getYTArtistTitle_ActualSong(self):
        """
        Verify that the YT utility pulls the metadata rows from a YT video
        """
        link = 'https://www.youtube.com/watch?v=LGdyVnW86SY'
        res = getYTArtistTitle(link)
        self.assertEqual(res['artist'], 'Steely Dan')
        self.assertEqual(res['title'], 'Bodhisattva')

    def test_getYTArtistTitle_GuessSongFormatted(self):
        """
        Verify that the YT utility guesses 'Artist - Title' from a non metadata link
        """
        link = 'https://www.youtube.com/watch?v=QbSV0qvAji4'
        res = getYTArtistTitle(link)
        self.assertEqual(res['artist'], 'Lonely')
        self.assertEqual(res['title'], 'Bee and puppycat')

    def test_getYTArtistTitle_GuessSongUnformatted(self):
        """
        Verify that the YT utility fills in the title from a non metadata non-' - ' link
        """
        link = 'https://www.youtube.com/watch?v=Y98XgZ9vGoQ'
        res = getYTArtistTitle(link)
        self.assertEqual(res['artist'], None)
        self.assertEqual(res['title'], 'Tenderly (Remastered)')
