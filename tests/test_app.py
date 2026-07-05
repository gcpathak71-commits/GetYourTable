import unittest

from app import app


class AppRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_success_route_accepts_restaurant_names_with_special_chars(self):
        response = self.client.get('/success?restaurant=Britannia%20%26%20Co.')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Reservation Confirmed', response.get_data(as_text=True))
        self.assertIn('Britannia &amp; Co.', response.get_data(as_text=True))

    def test_reserve_route_accepts_restaurant_names_with_slashes(self):
        response = self.client.get('/reserve?restaurant=Test%2FRestaurant')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
