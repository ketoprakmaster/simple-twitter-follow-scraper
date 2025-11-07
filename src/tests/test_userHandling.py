# tests/test_userHandling.py
import pytest
import json
import time
from unittest.mock import patch
from core.userHandling import (
    saveUsersRecord,
    compareRecentRecords,
    makeComparison,
    readFromRecords,
    returnAllRecords,
    processScrapeResults
)
from common.types import ComparisonResults, MODE
from common.exceptions import NotEnoughUserRecords
from core.userHandling import makeComparison

def test_saveUsersRecord_creates_file(tmp_path):
    username = "testuser"
    users = {"alice", "bob", "carol"}
    mode = MODE.following

    with patch("core.userHandling.USER_RECORDS_DIR", tmp_path):
        saveUsersRecord(username, mode, users)
        target_dir = tmp_path / username / mode
        files = list(target_dir.glob("*.json"))
        assert len(files) == 1

        # Check file content
        with files[0].open("r") as f:
            data = json.load(f)
            assert sorted(data["users"]) == sorted(users)

def test_compareRecentRecords_success(tmp_path):
    username = "testuser"
    mode = MODE.following
    users1 = {"user1", "user2", "user3"}
    users2 = {"user2", "user3", "user4"}

    with patch("core.userHandling.USER_RECORDS_DIR", tmp_path):
        saveUsersRecord(username, mode, users1)
        time.sleep(1)
        saveUsersRecord(username, mode, users2)

        result = compareRecentRecords(username, mode)

        assert result.added == {"user4"}
        assert result.removed == {"user1"}

def test_compareRecentRecords_not_enough_files(tmp_path):
    username = "notenough"
    mode = MODE.followers
    users = {"a", "b"}

    with patch("core.userHandling.USER_RECORDS_DIR", tmp_path):
        saveUsersRecord(username, mode, users)

        with pytest.raises(NotEnoughUserRecords):
            compareRecentRecords(username, mode)

def test_makeComparison_basic():
    past = {"a", "b", "c"}
    future = {"b", "c", "d"}

    result = makeComparison(past, future)

    assert result.added == {"d"}
    assert result.removed == {"a"}

def test_readFromRecords(tmp_path):
    users = ["u1", "u2"]
    file_path = tmp_path / "users.json"
    file_path.write_text(json.dumps({"users": users}))

    result = readFromRecords(file_path)

    assert set(result) == set(users)

def test_returnAllRecords_sorted(tmp_path):
    f1 = tmp_path / "2021-01-01.json"
    f2 = tmp_path / "2023-01-01.json"
    f3 = tmp_path / "2022-01-01.json"

    f1.write_text("[]")
    f2.write_text("[]")
    f3.write_text("[]")

    result = returnAllRecords(user_path=tmp_path)
    assert result == [f1, f3, f2]

def test_processScrapeResults_compare(tmp_path):
    users1 = set(["alice","bob"])
    users2 = set(["alice","bob","jared"])

    with patch("core.userHandling.USER_RECORDS_DIR", tmp_path):
        results = processScrapeResults(username="gary",mode=MODE.followers,new_users=users1)
        assert results.added == users1

        results = processScrapeResults(username="gary",mode=MODE.followers,new_users=users2)
        assert results.added == {"jared"}

        results = processScrapeResults(username="gary",mode=MODE.followers,new_users=users1)
        assert results.removed == {"jared"}
