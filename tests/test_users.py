def test_user_register_and_login(client, db_session):
    # register
    resp = client.post("/users/register", json={"username":"testu", "email":"t@example.com", "password":"secret"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testu"

    # login
    resp2 = client.post("/users/login", json={"username":"testu", "password":"secret"})
    assert resp2.status_code == 200
    token = resp2.json()["token"]
    assert token

    # token usage: create calc
    headers = {"Authorization": f"Bearer {token}"}
    resp3 = client.post("/calculations", json={"a":4,"b":2,"op_type":"Divide"}, headers=headers)
    assert resp3.status_code == 200
    calc_id = resp3.json()["id"]

    # read
    resp4 = client.get(f"/calculations/{calc_id}", headers=headers)
    assert resp4.status_code == 200
    assert resp4.json()["result"] == 2.0
