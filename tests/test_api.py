from fastapi.testclient import TestClient

from flop_nexus.api import app

client = TestClient(app)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_missions_exclude_social_farming() -> None:
    missions = client.get("/missions").json()
    titles = " ".join(m["title"].lower() for m in missions)
    assert "follow" not in titles
    assert "telegram" not in titles
    assert "repost" not in titles


def test_activity_rejects_non_did() -> None:
    response = client.get("/activity/not-a-did")
    assert response.status_code == 400


def test_activity_for_valid_unindexed_did() -> None:
    did = "did:key:z6MkpHhs1e4ffVgJh3cX9dqtyctx8m6FJqnJFiLxzZNGen8G"
    response = client.get(f"/activity/{did}")
    assert response.status_code == 200
    body = response.json()
    assert body["did"] == did
    assert body["indexed"] is False
    assert body["reward_status"] == "not_official"


def test_agent_manifest_is_independent() -> None:
    manifest = client.get("/.well-known/agent.json").json()
    assert manifest["official_flop_labs_product"] is False
