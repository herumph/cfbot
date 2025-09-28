import pytest
import json


@pytest.fixture
def game_with_pick_six():
    with open("data/tests/game_with_pick_six.json") as f:
        return json.load(f)
    

@pytest.fixture
def game_with_missed_pat():
    with open("data/tests/game_with_missed_pat.json") as f:
        return json.load(f)
    

@pytest.fixture
def game_with_safety():
    with open("data/tests/game_with_safety.json") as f:
        return json.load(f)
    

@pytest.fixture
def scoreboard():
    with open("data/tests/scoreboard.json") as f:
        return json.load(f)
    

@pytest.fixture
def boxscore():
    with open("data/tests/boxscore.json") as f:
        return json.load(f)