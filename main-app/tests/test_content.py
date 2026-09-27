import pytest
from unittest.mock import patch,MagicMock
from app.models.content import Content, ContentStatus

class TestContentCRUD:
    def test_list_content_public(self, client, published_content):
        response = client.get("/content/")
        assert response.status_code == 200
        data = response.json()
        assert "contents" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_list_content_filter_type(self, client, published_content):
        response = client.get("/content/?content_type=video")
        assert response.status_code == 200
        contents = response.json()["contents"]
        assert all(c["content_type"] == "video" for c in contents)

    def test_list_content_filter_category(self, client, published_content):
        response = client.get("/content/?category=Technology")
        assert response.status_code == 200

    def test_get_content_by_id(self, client, published_content):
        with patch("app.services.redis_service.track_view"):
            with patch("app.services.redis_service.get_view_count", return_value=5):
                with patch("app.services.redis_service.get_unique_views", return_value=3):
                    with patch("app.services.redis_service.get_likes_count", return_value=10):
                        response = client.get(f"/content/{published_content.id}")
        assert response.status_code == 200
        assert response.json()["id"] == published_content.id

    def test_get_nonexistent_content(self, client):
        response = client.get("/content/999")
        assert response.status_code == 404

    def test_creator_can_see_own_drafts(self, client, creator_headers, db, creator_user):
        draft = Content(
            title="Draft Content",
            content_type="article",
            status="draft",
            creator_id=creator_user.id
        )
        db.add(draft)
        db.commit()

        response = client.get("/content/my", headers=creator_headers)
        assert response.status_code == 200

    def test_viewer_cannot_upload(self, client, viewer_headers):
        response = client.post(
            "/content/upload",
            files={"file": ("test.mp4", b"fake video", "video/mp4")},
            data={
                "title": "Test Video",
                "content_type": "video"
            },
            headers=viewer_headers
        )
        assert response.status_code == 403

    def test_update_own_content(self, client, creator_headers, published_content):
        response = client.put(
            f"/content/{published_content.id}",
            json={"title": "Updated Title"},
            headers=creator_headers
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_delete_content(self, client, creator_headers, db, creator_user):
        content = Content(
            title="To Delete",
            content_type="article",
            status=ContentStatus.PUBLISHED,
            creator_id=creator_user.id
        )
        db.add(content)
        db.commit()

        with patch("app.services.s3_service.delete_from_s3"):
            response = client.delete(
                f"/content/{content.id}",
                headers=creator_headers
            )
        assert response.status_code == 204

class TestContentLikes:
    def test_like_content(self, client, creator_headers, published_content):
        with patch("app.services.redis_service.toggle_like") as mock_like:
            mock_like.return_value = {"action": "liked", "likes_count": 1}
            response = client.post(
                f"/content/{published_content.id}/like",
                headers=creator_headers
            )
        assert response.status_code == 200
        assert response.json()["action"] == "liked"

