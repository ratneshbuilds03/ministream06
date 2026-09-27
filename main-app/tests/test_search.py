import pytest

class TestSearch:
    def test_search_content(self,client,published_content):
        response = client.get("/search/content?q=python")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data

    def test_search_too_short(self,client):
        response = client.get("/search/content?q=a")
        assert response.status_code ==422
        
        
    def test_get_categories(self, client, published_content):
        response = client.get("/search/categories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_with_filters(self, client, published_content):
        response = client.get(
            "/search/content?q=python&content_type=video&sort_by=views"
        )
        assert response.status_code == 200

    def test_category_content(self, client, published_content):
        response = client.get("/search/category/Technology")
        assert response.status_code == 200
        assert "contents" in response.json()