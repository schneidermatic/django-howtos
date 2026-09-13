from django.test import TestCase


class CoreViewTests(TestCase):
    def test_http_request_is_redirected_to_https(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 301)
        self.assertTrue(response['Location'].startswith('https://'))

    def test_index_behind_proxy(self):
        # Nginx sets this header for requests that arrived via HTTPS
        response = self.client.get('/', headers={'X-Forwarded-Proto': 'https'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello from Django')

    def test_healthz_is_exempt_from_https_redirect(self):
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')
