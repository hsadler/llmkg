import datetime
import json
import logging
import uuid
from typing import Any, Generator

import asyncpg
import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockFixture

from app.database import Database, get_database
from app.main import app
from app.models import Item, ItemIn


@pytest.fixture
def client(mocker: MockFixture) -> Generator[TestClient, None, None]:
    def override_get_db() -> Any:
        return mocker.MagicMock(spec=Database)

    app.dependency_overrides[get_database] = override_get_db
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    yield TestClient(app)
    del app.dependency_overrides[get_database]


def get_mock_item(id: int) -> Item:
    return Item(
        id=id,
        uuid=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        created_at=datetime.datetime(2021, 8, 15, 18, 0),
        name="mock item",
        price=1.99,
    )


# GET ITEM TESTS


# test get_item status code
@pytest.mark.parametrize(
    "item_id, expected_status_code",
    [
        (1, 200),
        (2, 200),
        (0, 422),
        (-1, 422),
    ],
)
@pytest.mark.asyncio
async def test_get_item_found_status_code(
    client: TestClient, mocker: MockFixture, item_id: int, expected_status_code: int
) -> None:
    mock_item = get_mock_item(id=1)
    mocker.patch("app.routers.items.items_repo.fetch_item_by_id", return_value=mock_item)
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == expected_status_code


# test get_item response shape
@pytest.mark.parametrize(
    "item_id, expected_response",
    [
        (
            1,
            {
                "data": json.loads(get_mock_item(id=1).json()),
                "meta": {},
            },
        ),
        (
            2,
            {
                "data": json.loads(get_mock_item(id=2).json()),
                "meta": {},
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_item_found_response_shape(
    client: TestClient, mocker: MockFixture, item_id: int, expected_response: dict[str, Any]
) -> None:
    mock_item = get_mock_item(id=item_id)
    mocker.patch("app.routers.items.items_repo.fetch_item_by_id", return_value=mock_item)
    response = client.get(f"/api/items/{mock_item.id}")
    assert response.json() == expected_response


# test get_item not found status code
@pytest.mark.parametrize(
    "item_id, expected_status_code",
    [(3, 404), (4, 404)],
)
@pytest.mark.asyncio
async def test_get_item_not_found_status_code(
    client: TestClient, mocker: MockFixture, item_id: int, expected_status_code: int
) -> None:
    mock_item = None
    mocker.patch("app.routers.items.items_repo.fetch_item_by_id", return_value=mock_item)
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == expected_status_code


# test get_item exception status code
@pytest.mark.asyncio
async def test_get_item_exception_status_code(client: TestClient, mocker: MockFixture) -> None:
    mocker.patch("app.routers.items.items_repo.fetch_item_by_id", side_effect=asyncpg.DataError)
    response = client.get("/api/items/1")
    assert response.status_code == 500


# test get_item malformed id status code
@pytest.mark.parametrize(
    "item_id, expected_status_code",
    [("abc", 422), ("1.01", 422)],
)
@pytest.mark.asyncio
async def test_get_item_malformed_id_status_code(
    client: TestClient, mocker: MockFixture, item_id: str, expected_status_code: int
) -> None:
    mock_item = get_mock_item(id=1)
    mocker.patch("app.routers.items.items_repo.fetch_item_by_id", return_value=mock_item)
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == expected_status_code


# GET ITEMS TESTS


# test get_items status code
@pytest.mark.parametrize(
    "item_ids, expected_status_code",
    [
        ([1, 2], 200),
        ([1, 2, 3], 200),
        ([], 422),
        ([0], 422),
        ([-1], 422),
    ],
)
@pytest.mark.asyncio
async def test_get_items_found_status_code(
    client: TestClient, mocker: MockFixture, item_ids: list[int], expected_status_code: int
) -> None:
    mock_items = [get_mock_item(id=1) for _ in item_ids]
    mocker.patch("app.routers.items.items_repo.fetch_items_by_ids", return_value=mock_items)
    response = client.get("/api/items", params={"item_ids": item_ids})
    assert response.status_code == expected_status_code


# test get_items response shape
@pytest.mark.parametrize(
    "item_ids, expected_response",
    [
        (
            [1, 2],
            {
                "data": [
                    json.loads(get_mock_item(id=1).json()),
                    json.loads(get_mock_item(id=2).json()),
                ],
                "meta": {},
            },
        ),
        (
            [1, 2, 3],
            {
                "data": [
                    json.loads(get_mock_item(id=1).json()),
                    json.loads(get_mock_item(id=2).json()),
                    json.loads(get_mock_item(id=3).json()),
                ],
                "meta": {},
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_items_found_response_shape(
    client: TestClient, mocker: MockFixture, item_ids: list[int], expected_response: dict[str, Any]
) -> None:
    mock_items = [get_mock_item(id=id) for id in item_ids]
    mocker.patch("app.routers.items.items_repo.fetch_items_by_ids", return_value=mock_items)
    response = client.get("/api/items", params={"item_ids": item_ids})
    assert response.json() == expected_response


# test get_items when not found
@pytest.mark.asyncio
async def test_get_items_not_found(client: TestClient, mocker: MockFixture) -> None:
    mock_items: list[Item] = []
    mocker.patch("app.routers.items.items_repo.fetch_items_by_ids", return_value=mock_items)
    response = client.get("/api/items", params={"item_ids": [1, 2]})
    assert response.status_code == 200
    assert response.json() == {"data": [], "meta": {}}


# test get_items exception status code
@pytest.mark.asyncio
async def test_get_items_exception_status_code(client: TestClient, mocker: MockFixture) -> None:
    mocker.patch("app.routers.items.items_repo.fetch_items_by_ids", side_effect=asyncpg.DataError)
    response = client.get("/api/items", params={"item_ids": [1, 2]})
    assert response.status_code == 500


# test get_items malformed input status code
@pytest.mark.parametrize(
    "item_ids, expected_status_code",
    [
        ([1, "two"], 422),
        ([[1], 2, 3], 422),
        ([1, 2, {"three": 3}], 422),
    ],
)
@pytest.mark.asyncio
async def test_get_items_malformed_input_status_code(
    client: TestClient, mocker: MockFixture, item_ids: list[int], expected_status_code: int
) -> None:
    mock_items: list[Item] = []
    mocker.patch("app.routers.items.items_repo.fetch_items_by_ids", return_value=mock_items)
    response = client.get("/api/items", params={"item_ids": item_ids})
    assert response.status_code == expected_status_code


# CREATE ITEM TESTS


# test create_item success status code
@pytest.mark.parametrize(
    "item_in, expected_status_code",
    [
        (ItemIn(name="test item 1", price=1.0), 201),
        (ItemIn(name="test item 2", price=2.0), 201),
    ],
)
@pytest.mark.asyncio
async def test_create_item_success_status_code(
    client: TestClient, mocker: MockFixture, item_in: ItemIn, expected_status_code: int
) -> None:
    mocker.patch("app.routers.items.items_repo.create_item", return_value=get_mock_item(id=1))
    response = client.post("/api/items", json={"data": json.loads(item_in.json())})
    assert response.status_code == expected_status_code


# test create_item success response shape
@pytest.mark.parametrize(
    "item_in, item_id, expected_response",
    [
        (
            ItemIn(name="test item 1", price=1.0),
            1,
            {
                "data": json.loads(get_mock_item(id=1).json()),
                "meta": {"created": True},
            },
        ),
        (
            ItemIn(name="test item 2", price=2.0),
            2,
            {
                "data": json.loads(get_mock_item(id=2).json()),
                "meta": {"created": True},
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_item_success_response_shape(
    client: TestClient,
    mocker: MockFixture,
    item_in: ItemIn,
    item_id: int,
    expected_response: dict[str, Any],
) -> None:
    mocker.patch("app.routers.items.items_repo.create_item", return_value=get_mock_item(id=item_id))
    response = client.post("/api/items", json={"data": json.loads(item_in.json())})
    assert response.json() == expected_response


# test create item exception status code
@pytest.mark.parametrize(
    "item_in, expected_status_code",
    [
        (ItemIn(name="test item 1", price=1.0), 500),
        (ItemIn(name="test item 2", price=2.0), 500),
    ],
)
@pytest.mark.asyncio
async def test_create_item_exception_status_code(
    client: TestClient, mocker: MockFixture, item_in: ItemIn, expected_status_code: int
) -> None:
    mocker.patch("app.routers.items.items_repo.create_item", side_effect=Exception)
    response = client.post("/api/items", json={"data": json.loads(item_in.json())})
    assert response.status_code == expected_status_code


# test create item when item already exists
@pytest.mark.asyncio
async def test_create_item_already_exists(client: TestClient, mocker: MockFixture) -> None:
    mocker.patch(
        "app.routers.items.items_repo.create_item",
        side_effect=asyncpg.exceptions.UniqueViolationError,
    )
    response = client.post(
        "/api/items", json={"data": json.loads(ItemIn(name="test item 1", price=1.0).json())}
    )
    assert response.status_code == 409


# test create item malformed input status code
@pytest.mark.parametrize(
    "input_data, expected_status_code",
    [
        ({}, 422),
        ({"foo": "bar"}, 422),
        ({"data": "malformed"}, 422),
        ({"data": {"foo": "bar"}}, 422),
    ],
)
@pytest.mark.asyncio
async def test_create_item_malformed_input_status_code(
    client: TestClient, mocker: MockFixture, input_data: dict[str, Any], expected_status_code: int
) -> None:
    mocker.patch("app.routers.items.items_repo.create_item", return_value=[])
    response = client.post("/api/items", json=input_data)
    assert response.status_code == expected_status_code
