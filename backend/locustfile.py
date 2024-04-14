import uuid

from locust import HttpUser, tag, task


class User(HttpUser):
    @task
    @tag("status")
    def status(self) -> None:
        self.client.get("/status")

    @task
    @tag("long-running")
    def fibonacci(self) -> None:
        self.client.get("/api/example/long-running/fibonacci/20")

    @task
    @tag("item")
    def create_then_get_item(self) -> None:
        res = self.client.post(
            "/api/items", json={"data": {"name": str(uuid.uuid4()), "price": "101.01"}}
        )
        item_id = res.json()["data"]["id"]
        self.client.get(f"/api/items/{item_id}")

    @task
    @tag("items")
    def create_then_get_items(self) -> None:
        item_ids = []
        for _ in range(5):
            res = self.client.post(
                "/api/items", json={"data": {"name": str(uuid.uuid4()), "price": "101.01"}}
            )
            item_ids.append(res.json()["data"]["id"])
        self.client.get(f"/api/items?{'&'.join([f'item_ids={item_id}' for item_id in item_ids])}")
