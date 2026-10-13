import pytest
from app import create_app

@pytest.fixture
def client(tmp_path):
    app=create_app({"TESTING":True,"DATABASE":str(tmp_path/"test.db"),"SECRET_KEY":"test"})
    with app.test_client() as c: yield c

def test_home_and_health(client):
    assert client.get("/").status_code==200
    assert client.get("/health").get_json()=={"status":"ok"}

def test_add_book_and_member(client):
    r=client.post("/books",data={"title":"Clean Code","author":"Robert Martin","copies":"2"},follow_redirects=True)
    assert b"Clean Code" in r.data
    r=client.post("/members",data={"name":"Demo Member","email":"demo@example.com"},follow_redirects=True)
    assert b"Member registered" in r.data

def test_issue_and_return(client):
    client.post("/books",data={"title":"DevOps Handbook","author":"Gene Kim","copies":"1"})
    client.post("/members",data={"name":"Test Member","email":"test@example.com"})
    r=client.post("/issue/1",data={"member_id":"1"},follow_redirects=True)
    assert b"Book issued" in r.data
    r=client.post("/return/1",follow_redirects=True)
    assert b"Book returned" in r.data
