def test_register_creates_owner(client):
    resp = client.post(
        "/auth/register",
        json={
            "tenant_slug": "acme",
            "tenant_name": "ACME Corp",
            "email": "owner@acme.io",
            "password": "supersecret123",
            "full_name": "Alice Owner",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "OWNER"
    assert body["email"] == "owner@acme.io"


def test_duplicate_tenant_slug_rejected(client):
    payload = {
        "tenant_slug": "globex",
        "tenant_name": "Globex",
        "email": "owner@globex.io",
        "password": "supersecret123",
        "full_name": "Bob Owner",
    }
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_login_and_me(client):
    client.post(
        "/auth/register",
        json={
            "tenant_slug": "initech",
            "tenant_name": "Initech",
            "email": "owner@initech.io",
            "password": "supersecret123",
            "full_name": "Carl Owner",
        },
    )
    login_resp = client.post(
        "/auth/login",
        json={"tenant_slug": "initech", "email": "owner@initech.io", "password": "supersecret123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "owner@initech.io"


def test_login_wrong_password_rejected(client):
    client.post(
        "/auth/register",
        json={
            "tenant_slug": "wayne",
            "tenant_name": "Wayne Enterprises",
            "email": "owner@wayne.io",
            "password": "supersecret123",
            "full_name": "Bruce Owner",
        },
    )
    resp = client.post(
        "/auth/login",
        json={"tenant_slug": "wayne", "email": "owner@wayne.io", "password": "wrongpassword"},
    )
    assert resp.status_code == 401
