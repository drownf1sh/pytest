import pytest
from app.main import create_app

client = create_app(config_name="test").test_client()


class TestPingController:
    def test_ping_controller(self):
        response = client.get("/api/rec/ping")
        print("response:", response)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main()
