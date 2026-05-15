import pytest
import json
from common.types import MODE
from models.users import UserRecords, UserSnapshot
from common.exceptions import FiledecodeError

@pytest.fixture
def mock_records_dir(tmp_path, monkeypatch):
    """Mocks the USER_RECORDS_DIR to a temporary folder for testing."""
    monkeypatch.setattr("models.users.USER_RECORDS_DIR", tmp_path)
    return tmp_path

def test_snapshot_save(mock_records_dir):
    users = {"alice", "bob"}
    snap = UserSnapshot("testuser", MODE.following, users, timestamp="2024.01.01")
    snap.save()

    expected_path = mock_records_dir / "testuser" / MODE.following / "2024.01.01.json"
    assert expected_path.exists()

    with open(expected_path) as f:
        data = json.load(f)
        assert set(data["users"]) == users

def test_records_indexing(mock_records_dir):
    username = "testuser"
    mode = MODE.following
    record_path = mock_records_dir / username / mode
    record_path.mkdir(parents=True)

    # Create two dummy records
    (record_path / "2024.01.01.00.00.01.json").write_text(json.dumps({"users": ["a"]}))
    (record_path / "2024.01.01.00.00.02.json").write_text(json.dumps({"users": ["a", "b"]}))

    history = UserRecords(username, mode)

    # Test __len__
    history.refresh()
    assert len(history) == 2

    # Test __getitem__ (index 0 is the older one due to sorting)
    snap = history[0]
    assert isinstance(snap, UserSnapshot)
    assert snap.users == {"a"}
    assert snap.timestamp == "2024.01.01.00.00.01"

def test_snapshot_subtraction():
    old = UserSnapshot("u", MODE.following, {"stay", "gone"})
    new = UserSnapshot("u", MODE.following, {"stay", "new"})

    diff = new - old

    assert diff.added == {"new"}
    # Note: adjust this based on how your UserStatus enum works
    assert "gone" in diff.removed

def test_load_snapshot_error(mock_records_dir):
    username = "testuser"
    mode = MODE.following
    record_path = mock_records_dir / username / mode
    record_path.mkdir(parents=True)

    bad_file = record_path / "corrupt.json"
    bad_file.write_text("not json content")

    history = UserRecords(username, mode)
    with pytest.raises(FiledecodeError): # Replace with your FiledecodeError
        history.load_snapshot(bad_file)
