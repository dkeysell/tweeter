import doctest
import unittest
import time
import tweeter.app as app


class TestPhase(unittest.TestCase):

    def test_get_links(self):
        links = app.get_links()
        for link in links:
            print(link)

    def test_expire_link_cache(self):
        app.link_cache.append(('retain', time.time()))
        app.link_cache.append(('expire', time.time()-(app.cache_timeout+1)))
        app.time_expire_cache()
        self.assertEqual(1, len(app.link_cache))

    def test_get_text(self):
        links = app.get_links()
        for link in links:
            text = app.get_text(link)
            if text is not None:
                sentences = app.summarise(text, 3)
                for sentence in sentences:
                    print(sentence)


if __name__ == "__main__":
    unittest.main()
    doctest.testmod()
