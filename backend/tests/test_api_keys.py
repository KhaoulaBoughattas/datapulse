def _register_and_login_owner(client, slug: str):
    client.post("/auth/register", json={"tenant_slug": slug, "tenant_name": slug.upper(), "email": f"owner@{slug}.io", "password": "supersecret123", "full_name": "Owner"})
    resp = client.post("/auth/login", json={"tenant_slug": slug, "email": f"owner@{slug}.io", "password": "supersecret123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_api_key_created_and_authenticates(client):
    owner_headers = _register_and_login_owner(client, "keytest")
    create_resp = client.post("/api-keys", json={"name": "Airflow DAG key"}, headers=owner_headers)
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["raw_key"].startswith("dp_live_")

    api_key_headers = {"Authorization": f"Bearer {body['raw_key']}"}
    me_resp = client.get("/pipelines", headers=api_key_headers)
    assert me_resp.status_code == 200


def test_api_key_list_never_returns_raw_key(client):
    owner_headers = _register_and_login_owner(client, "keytest2")
    client.post("/api-keys", json={"name": "test"}, headers=owner_headers)
    list_resp = client.get("/api-keys", headers=owner_headers)
    assert list_resp.status_code == 200
    for key in list_resp.json():
        assert "raw_key" not in key


def test_revoked_api_key_no_longer_authenticates(client):
    owner_headers = _register_and_login_owner(client, "keytest3")
    create_resp = client.post("/api-keys", json={"name": "test"}, headers=owner_headers)
    key_id = create_resp.json()["id"]
    raw_key = create_resp.json()["raw_key"]

    revoke_resp = client.delete(f"/api-keys/{key_id}", headers=owner_headers)
    assert revoke_resp.status_code == 204

    api_key_headers = {"Authorization": f"Bearer {raw_key}"}
    resp = client.get("/pipelines", headers=api_key_headers)
    assert resp.status_code == 401
