def _register_and_login_owner(client, slug: str) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={
            "tenant_slug": slug,
            "tenant_name": slug.upper(),
            "email": f"owner@{slug}.io",
            "password": "supersecret123",
            "full_name": "Owner",
        },
    )
    resp = client.post(
        "/auth/login", json={"tenant_slug": slug, "email": f"owner@{slug}.io", "password": "supersecret123"}
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_viewer_cannot_write_but_can_read(client):
    owner_headers = _register_and_login_owner(client, "rbactest")

    create_user_resp = client.post(
        "/users",
        json={
            "email": "viewer@rbactest.io",
            "password": "supersecret123",
            "full_name": "Viewer Vera",
            "role": "VIEWER",
        },
        headers=owner_headers,
    )
    assert create_user_resp.status_code == 201

    login_resp = client.post(
        "/auth/login",
        json={"tenant_slug": "rbactest", "email": "viewer@rbactest.io", "password": "supersecret123"},
    )
    viewer_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    create_pipeline_resp = client.post(
        "/pipelines", json={"name": "Viewer's pipeline", "pipeline_type": "BATCH"}, headers=viewer_headers
    )
    assert create_pipeline_resp.status_code == 403

    list_resp = client.get("/pipelines", headers=viewer_headers)
    assert list_resp.status_code == 200


def test_viewer_cannot_list_users(client):
    owner_headers = _register_and_login_owner(client, "rbactest2")
    client.post(
        "/users",
        json={
            "email": "viewer2@rbactest2.io",
            "password": "supersecret123",
            "full_name": "Viewer",
            "role": "VIEWER",
        },
        headers=owner_headers,
    )
    login_resp = client.post(
        "/auth/login",
        json={"tenant_slug": "rbactest2", "email": "viewer2@rbactest2.io", "password": "supersecret123"},
    )
    viewer_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    assert client.get("/users", headers=viewer_headers).status_code == 403
