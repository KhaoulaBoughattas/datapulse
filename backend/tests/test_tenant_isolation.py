def _register_and_login(client, slug: str, name: str) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={
            "tenant_slug": slug,
            "tenant_name": name,
            "email": f"owner@{slug}.io",
            "password": "supersecret123",
            "full_name": "Owner",
        },
    )
    resp = client.post(
        "/auth/login", json={"tenant_slug": slug, "email": f"owner@{slug}.io", "password": "supersecret123"}
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_pipeline_cross_tenant_isolation(client):
    headers_a = _register_and_login(client, "tenanta", "Tenant A")
    headers_b = _register_and_login(client, "tenantb", "Tenant B")

    create_resp = client.post(
        "/pipelines", json={"name": "A's daily orders pipeline", "pipeline_type": "BATCH"}, headers=headers_a
    )
    assert create_resp.status_code == 201
    pipeline_id = create_resp.json()["id"]

    assert client.get(f"/pipelines/{pipeline_id}", headers=headers_b).status_code == 404

    list_resp = client.get("/pipelines", headers=headers_b)
    assert list_resp.status_code == 200
    assert all(p["id"] != pipeline_id for p in list_resp.json())

    assert client.get(f"/pipelines/{pipeline_id}", headers=headers_a).status_code == 200


def test_pipeline_cannot_reference_other_tenants_data_source(client):
    headers_a = _register_and_login(client, "tenantc", "Tenant C")
    headers_b = _register_and_login(client, "tenantd", "Tenant D")

    ds_resp = client.post(
        "/data-sources",
        json={"name": "B's Postgres", "source_type": "POSTGRES", "connection_config": {}},
        headers=headers_b,
    )
    assert ds_resp.status_code == 201
    other_tenants_data_source_id = ds_resp.json()["id"]

    resp = client.post(
        "/pipelines",
        json={
            "name": "Sneaky pipeline",
            "pipeline_type": "BATCH",
            "data_source_id": other_tenants_data_source_id,
        },
        headers=headers_a,
    )
    assert resp.status_code == 404
