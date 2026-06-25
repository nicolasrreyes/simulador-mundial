import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base
from repositories.user_repository import UserRepository
from repositories.team_repository import TeamRepository
from repositories.player_repository import PlayerRepository
from schemas.user import UserCreate
from schemas.team import TeamCreate
from schemas.player import PlayerCreate

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)


# =============================================================================
# UserRepository
# =============================================================================

def test_user_repo_create(db_session):
    repo = UserRepository(db_session)
    user = repo.create(UserCreate(name="Juan", email="juan@test.com"))
    assert user.id is not None
    assert user.name == "Juan"
    assert user.email == "juan@test.com"


def test_user_repo_get_by_email(db_session):
    repo = UserRepository(db_session)
    repo.create(UserCreate(name="Juan", email="juan@test.com"))
    found = repo.get_by_email("juan@test.com")
    assert found is not None
    assert found.name == "Juan"


def test_user_repo_get_by_email_not_found(db_session):
    repo = UserRepository(db_session)
    assert repo.get_by_email("no@existe.com") is None


def test_user_repo_get_all(db_session):
    repo = UserRepository(db_session)
    repo.create(UserCreate(name="Juan", email="juan@test.com"))
    repo.create(UserCreate(name="Maria", email="maria@test.com"))
    users = repo.get_all()
    assert len(users) == 2


def test_user_repo_update(db_session):
    repo = UserRepository(db_session)
    user = repo.create(UserCreate(name="Juan", email="juan@test.com"))
    updated = repo.update(user, {"name": "Juan Updated"})
    assert updated.name == "Juan Updated"
    assert updated.email == "juan@test.com"


def test_user_repo_delete(db_session):
    repo = UserRepository(db_session)
    user = repo.create(UserCreate(name="Juan", email="juan@test.com"))
    repo.delete(user)
    assert repo.get_by_id(user.id) is None


def test_user_repo_get_by_id_not_found(db_session):
    repo = UserRepository(db_session)
    assert repo.get_by_id(999) is None


# =============================================================================
# TeamRepository
# =============================================================================

def test_team_repo_create(db_session):
    repo = TeamRepository(db_session)
    team = repo.create(TeamCreate(name="Argentina", code="ARG"))
    assert team.id is not None
    assert team.name == "Argentina"
    assert team.code == "ARG"


def test_team_repo_get_by_code(db_session):
    repo = TeamRepository(db_session)
    repo.create(TeamCreate(name="Argentina", code="ARG"))
    found = repo.get_by_code("ARG")
    assert found is not None
    assert found.name == "Argentina"


def test_team_repo_get_by_code_not_found(db_session):
    repo = TeamRepository(db_session)
    assert repo.get_by_code("XXX") is None


def test_team_repo_get_by_name(db_session):
    repo = TeamRepository(db_session)
    repo.create(TeamCreate(name="Argentina", code="ARG"))
    found = repo.get_by_name("Argentina")
    assert found is not None


def test_team_repo_get_by_name_not_found(db_session):
    repo = TeamRepository(db_session)
    assert repo.get_by_name("NoExiste") is None


def test_team_repo_count(db_session):
    repo = TeamRepository(db_session)
    assert repo.count() == 0
    repo.create(TeamCreate(name="Argentina", code="ARG"))
    repo.create(TeamCreate(name="Brasil", code="BRA"))
    assert repo.count() == 2


def test_team_repo_update_group(db_session):
    repo = TeamRepository(db_session)
    team = repo.create(TeamCreate(name="Argentina", code="ARG"))
    updated = repo.update(team, {"group_name": "A"})
    assert updated.group_name == "A"


def test_team_repo_delete(db_session):
    repo = TeamRepository(db_session)
    team = repo.create(TeamCreate(name="Argentina", code="ARG"))
    repo.delete(team)
    assert repo.get_by_id(team.id) is None


# =============================================================================
# PlayerRepository
# =============================================================================

def test_player_repo_create(db_session):
    team_repo = TeamRepository(db_session)
    team = team_repo.create(TeamCreate(name="Argentina", code="ARG"))
    repo = PlayerRepository(db_session)
    player = repo.create(PlayerCreate(name="Messi", position="FW", team_id=team.id))
    assert player.id is not None
    assert player.name == "Messi"
    assert player.position == "FW"


def test_player_repo_get_all_by_team(db_session):
    team_repo = TeamRepository(db_session)
    team = team_repo.create(TeamCreate(name="Argentina", code="ARG"))
    repo = PlayerRepository(db_session)
    repo.create(PlayerCreate(name="Messi", position="FW", team_id=team.id))
    repo.create(PlayerCreate(name="Di Maria", position="MF", team_id=team.id))
    players = repo.get_all(team_id=team.id)
    assert len(players) == 2


def test_player_repo_get_all_no_filter(db_session):
    team_repo = TeamRepository(db_session)
    t1 = team_repo.create(TeamCreate(name="Argentina", code="ARG"))
    t2 = team_repo.create(TeamCreate(name="Brasil", code="BRA"))
    repo = PlayerRepository(db_session)
    repo.create(PlayerCreate(name="Messi", position="FW", team_id=t1.id))
    repo.create(PlayerCreate(name="Neymar", position="FW", team_id=t2.id))
    assert len(repo.get_all()) == 2


def test_player_repo_count_by_team(db_session):
    team_repo = TeamRepository(db_session)
    team = team_repo.create(TeamCreate(name="Argentina", code="ARG"))
    repo = PlayerRepository(db_session)
    assert repo.count_by_team(team.id) == 0
    repo.create(PlayerCreate(name="Messi", position="FW", team_id=team.id))
    assert repo.count_by_team(team.id) == 1


def test_player_repo_delete(db_session):
    team_repo = TeamRepository(db_session)
    team = team_repo.create(TeamCreate(name="Argentina", code="ARG"))
    repo = PlayerRepository(db_session)
    player = repo.create(PlayerCreate(name="Messi", position="FW", team_id=team.id))
    repo.delete(player)
    assert repo.get_by_id(player.id) is None
