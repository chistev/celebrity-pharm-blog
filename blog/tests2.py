from django.test import TestCase, Client
from django.urls import reverse
from django.core.signing import TimestampSigner
from django.utils import timezone
from blog.models import Subscriber

class ConfirmSubscriptionViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signer = TimestampSigner()
        self.email = "test@example.com"
        self.valid_token = self.signer.sign(self.email)
        self.url = reverse("confirm_subscription")

    def test_happy_path_valid_token(self):
        """Test that a valid token processes correctly and does not trigger the 'if not token' condition."""
        # Create a subscriber to simulate a real scenario
        Subscriber.objects.create(email=self.email, is_confirmed=False)

        # Make a GET request with a valid token
        response = self.client.get(self.url, {"token": self.valid_token})

        # Check that the response does not render subscription_invalid.html
        self.assertNotEqual(response.status_code, 400)
        self.assertTemplateNotUsed(response, "blog/subscription_invalid.html")

        # Verify the subscriber is confirmed
        subscriber = Subscriber.objects.get(email=self.email)
        self.assertTrue(subscriber.is_confirmed)
        self.assertEqual(subscriber.confirmation_token, self.valid_token)
        self.assertRedirects(response, reverse("subscription_success"))

    def test_unhappy_path_no_token(self):
        """Test that no token in the request triggers the 'if not token' condition."""
        # Make a GET request without a token
        response = self.client.get(self.url)

        # Check that the response renders subscription_invalid.html with status 400
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "blog/subscription_invalid.html")

    def test_edge_case_empty_token(self):
        """Test that an empty token parameter triggers the 'if not token' condition."""
        # Make a GET request with an empty token
        response = self.client.get(self.url, {"token": ""})

        # Check that the response renders subscription_invalid.html with status 400
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "blog/subscription_invalid.html")