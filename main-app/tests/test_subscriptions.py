import pytest
from unittest.mock import patch, AsyncMock

class TestSubscriptions:
    def test_follow_creator(self, client, viewer_headers, creator_user):
        with patch("app.services.notification_client.notify_new_follower", new_callable=AsyncMock):
            response = client.post(
                f"/subscriptions/follow/{creator_user.id}",
                headers=viewer_headers
            )
        assert response.status_code == 200
        assert "following" in response.json()["message"].lower()

    def test_cannot_follow_self(self, client, creator_headers, creator_user):
        with patch("app.services.notification_client.notify_new_follower", new_callable=AsyncMock):
            response = client.post(
                f"/subscriptions/follow/{creator_user.id}",
                headers=creator_headers
            )
        assert response.status_code == 400
        assert "yourself" in response.json()["detail"].lower()

    def test_cannot_follow_twice(self, client, viewer_headers, creator_user):
        with patch("app.services.notification_client.notify_new_follower", new_callable=AsyncMock):
            client.post(
                f"/subscriptions/follow/{creator_user.id}",
                headers=viewer_headers
            )
            response = client.post(
                f"/subscriptions/follow/{creator_user.id}",
                headers=viewer_headers
            )
        assert response.status_code == 400

    def test_unfollow_creator(self, client, viewer_headers, creator_user, db, viewer_user):
        from app.models.subscription import Subscription
        sub = Subscription(
            subscriber_id=viewer_user.id,
            creator_id=creator_user.id
        )
        db.add(sub)
        db.commit()

        response = client.delete(
            f"/subscriptions/unfollow/{creator_user.id}",
            headers=viewer_headers
        )
        assert response.status_code == 200

    def test_check_following_status(self, client, viewer_headers, creator_user):
        response = client.get(
            f"/subscriptions/check/{creator_user.id}",
            headers=viewer_headers
        )
        assert response.status_code == 200
        assert "is_following" in response.json()

    def test_get_followers_list(self, client, creator_user):
        response = client.get(f"/subscriptions/followers/{creator_user.id}")
        assert response.status_code == 200
        assert "followers" in response.json()

    def test_get_following_list(self, client, viewer_headers):
        response = client.get(
            "/subscriptions/my/following",
            headers=viewer_headers
        )
        assert response.status_code == 200

    def test_subscription_stats(self, client, creator_user):
        response = client.get(f"/subscriptions/stats/{creator_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert "followers" in data
        assert "following" in data