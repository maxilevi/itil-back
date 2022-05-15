
def test_index(client):
    response = client.get("/")
    assert b"Hola" in response.data