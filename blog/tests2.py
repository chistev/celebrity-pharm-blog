import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.core.signing import TimestampSigner
from django.utils import timezone

from unittest.mock import patch

import time

from blog.models import Subscriber, UnsubscribeToken

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

    def test_signature_expired(self):
        """Test that an expired token triggers the SignatureExpired condition."""
        # Create a token and mock the timestamp to be older than 1 hour
        with patch('django.core.signing.time.time') as mock_time:
            # Set the time to 2 hours ago (7200 seconds > 3600 seconds max_age)
            mock_time.return_value = time.time() - 7200
            expired_token = self.signer.sign(self.email)

        # Now make a request with the expired token
        response = self.client.get(self.url, {"token": expired_token})

        # Check that the response renders subscription_expired.html with status 400
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "blog/subscription_expired.html")

    def test_bad_signature(self):
        """Test that an invalid token triggers the BadSignature condition."""
        # Create an invalid token by modifying a valid one (e.g., appending junk)
        invalid_token = self.valid_token + "invalid"

        # Make a request with the invalid token
        response = self.client.get(self.url, {"token": invalid_token})

        # Check that the response renders subscription_invalid.html with status 400
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "blog/subscription_invalid.html")

class HandleUnsubscribeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "test@example.com"
        self.url = reverse("handle-unsubscribe")
        # Create a subscriber and an unsubscribe token for testing
        self.subscriber = Subscriber.objects.create(
            email=self.email,
            is_confirmed=True,
            confirmation_token="dummy_token",
            token_created_at=timezone.now()
        )
        self.token = UnsubscribeToken.objects.create(
            email=self.email,
            token=uuid.uuid4(),
            created_at=timezone.now(),
            unsubscribed=False
        )

    # === YOUR ORIGINAL TESTS ===
    def test_happy_path_valid_token(self):
        """Test that a valid token processes correctly and does not trigger the 'if not token_value' condition."""
        response = self.client.get(self.url, {"token": str(self.token.token)})
        self.assertRedirects(response, reverse("unsubscribe-status", kwargs={"status": "success"}))
        # Verify the subscriber is deleted
        self.assertFalse(Subscriber.objects.filter(email=self.email).exists())
        # Verify the token is marked as unsubscribed
        self.token.refresh_from_db()
        self.assertTrue(self.token.unsubscribed)

    def test_unhappy_path_no_token(self):
        """Test that no token in the request triggers the 'if not token_value' condition."""
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("unsubscribe-status", kwargs={"status": "invalid"}))
        # Verify the subscriber is not deleted
        self.assertTrue(Subscriber.objects.filter(email=self.email).exists())
        # Verify the token is not marked as unsubscribed
        self.token.refresh_from_db()
        self.assertFalse(self.token.unsubscribed)

    def test_edge_case_empty_token(self):
        """Test that an empty token parameter triggers the 'if not token_value' condition."""
        response = self.client.get(self.url, {"token": ""})
        self.assertRedirects(response, reverse("unsubscribe-status", kwargs={"status": "invalid"}))
        # Verify the subscriber is not deleted
        self.assertTrue(Subscriber.objects.filter(email=self.email).exists())
        # Verify the token is not marked as unsubscribed
        self.token.refresh_from_db()
        self.assertFalse(self.token.unsubscribed)

    # === NEW TESTS I ADDED ===
    def test_unhappy_path_nonexistent_token(self):
        """Test that a non-existent token triggers the DoesNotExist branch."""
        fake_token = uuid.uuid4()  # Token that doesn't exist in DB
        response = self.client.get(self.url, {"token": str(fake_token)})
        self.assertRedirects(response, reverse("unsubscribe-status", kwargs={"status": "invalid"}))
        # Subscriber should remain
        self.assertTrue(Subscriber.objects.filter(email=self.email).exists())
        # Original token should remain unchanged
        self.token.refresh_from_db()
        self.assertFalse(self.token.unsubscribed)

    def test_edge_case_malformed_token(self):
        """Test that a malformed token (not a UUID) triggers the DoesNotExist branch."""
        response = self.client.get(self.url, {"token": "not-a-uuid"})
        self.assertRedirects(response, reverse("unsubscribe-status", kwargs={"status": "invalid"}))
        # Subscriber should remain
        self.assertTrue(Subscriber.objects.filter(email=self.email).exists())
        # Token should remain unchanged
        self.token.refresh_from_db()
        self.assertFalse(self.token.unsubscribed)

    def test_expired_token_redirects(self):
        """Token older than 24 hours should redirect to expired."""
        self.token.created_at = timezone.now() - timezone.timedelta(days=2)
        self.token.save()
        response = self.client.get(self.url, {"token": str(self.token.token)})
        self.assertRedirects(response, reverse("unsubscribe-status", kwargs={"status": "expired"}))
        # Subscriber still exists, token unchanged
        self.assertTrue(Subscriber.objects.filter(email=self.email).exists())
        self.token.refresh_from_db()
        self.assertFalse(self.token.unsubscribed)

    def test_already_unsubscribed_redirects(self):
        """Token already marked as unsubscribed should redirect to already."""
        self.token.unsubscribed = True
        self.token.save()
        response = self.client.get(self.url, {"token": str(self.token.token)})
        self.assertRedirects(response, reverse("unsubscribe-status", kwargs={"status": "already"}))
        # Subscriber remains deleted/not recreated
        self.assertTrue(Subscriber.objects.filter(email=self.email).exists())  # wasn't deleted again
        self.token.refresh_from_db()
        self.assertTrue(self.token.unsubscribed)

    def test_edge_case_expired_and_unsubscribed(self):
        """Edge case: token is both expired and unsubscribed; expired takes precedence."""
        self.token.unsubscribed = True
        self.token.created_at = timezone.now() - timezone.timedelta(days=2)
        self.token.save()
        response = self.client.get(self.url, {"token": str(self.token.token)})
        self.assertRedirects(response, reverse("unsubscribe-status", kwargs={"status": "expired"}))
        self.assertTrue(Subscriber.objects.filter(email=self.email).exists())
        self.token.refresh_from_db()
        self.assertTrue(self.token.unsubscribed)
