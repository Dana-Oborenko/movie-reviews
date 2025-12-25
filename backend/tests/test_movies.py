def test_movies_crud(client):
    # Create
    r = client.post("/movies", json={"title": "Matrix", "description": "Sci-fi"})
    assert r.status_code == 201
    movie = r.json()
    assert movie["title"] == "Matrix"

    # List
    r = client.get("/movies")
    assert r.status_code == 200
    items = r.json()
    assert any(m["title"] == "Matrix" for m in items)

    # Get by id
    r = client.get(f"/movies/{movie['id']}")
    assert r.status_code == 200

    # Update
    r = client.put(f"/movies/{movie['id']}", json={"title": "Matrix 1", "description": "Neo"})
    assert r.status_code == 200
    assert r.json()["title"] == "Matrix 1"

    # Delete
    r = client.delete(f"/movies/{movie['id']}")
    assert r.status_code == 204
