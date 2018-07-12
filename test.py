import unittest
from tripadvisor.spiders import tripadvisor

class Test(unittest.TestCase):

    def test_review_next_page(self):
        url = 'https://www.tripadvisor.cn/Restaurant_Review-g294217-d1028680-Reviews-Aqua_Luna-Hong_Kong.html'
        new_url = tripadvisor.review_next_page(url, 12)
        expect = 'https://www.tripadvisor.cn/Restaurant_Review-g294217-d1028680-Reviews-or10-Aqua_Luna-Hong_Kong.html'
        self.assertEqual(new_url, expect)
        url = 'https://www.tripadvisor.cn/Restaurant_Review-g294217-d1028680-Reviews-or10-Aqua_Luna-Hong_Kong.html'
        new_url = tripadvisor.review_next_page(url, 12)
        self.assertEqual(new_url, None)
        url = 'https://www.tripadvisor.cn/Restaurant_Review-g294217-d1028680-Reviews-or20-Aqua_Luna-Hong_Kong.html'
        new_url = tripadvisor.review_next_page(url, 30)
        self.assertEqual(new_url, None)
        url = 'https://www.tripadvisor.cn/Restaurant_Review-g294217-d1028680-Reviews-or20-Aqua_Luna-Hong_Kong.html'
        new_url = tripadvisor.review_next_page(url, 35)
        expect = 'https://www.tripadvisor.cn/Restaurant_Review-g294217-d1028680-Reviews-or30-Aqua_Luna-Hong_Kong.html'
        self.assertEqual(new_url, expect)

if __name__ == '__main__':
    unittest.main()


