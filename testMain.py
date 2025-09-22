import unittest
import browser_cookie3
cookies = browser_cookie3.librewolf()
headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
}
from main import (
   get_stocks_from_index 
)

stock = 'TRIDENT'
class DataRetrievalTest2(unittest.TestCase):
    # test if the function creates a screener.html file
    def testIsItAList(self):
        path = 'data/' + stock + 'screener.html'


if __name__ == '__main__':
    unittest.main()
