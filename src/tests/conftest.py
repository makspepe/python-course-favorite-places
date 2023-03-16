import os
from pathlib import Path
from uuid import uuid4

import pytest_asyncio
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy_utils import create_database, drop_database
from sqlmodel import SQLModel

from integrations.db.session import get_session
from main import app
from settings import settings

PROJECT_PATH = Path(__file__).parent.parent.resolve()


@pytest_asyncio.fixture
async def session():
    """
    Фикстура тестовой сессии для работы с базой данных.
    После тестирования изменения, сделанные в БД не сохраняются.
    :return:
    """

    db_id = uuid4().hex
    db_name = settings.database_url + db_id
    os.environ["DATABASE_URL"] = db_name
    create_database(settings.database_sync + db_id)
    db_engine = create_async_engine(db_name, echo=True, future=True)

    async with db_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    connection = await db_engine.connect()
    transaction = await connection.begin()

    async_session = AsyncSession(bind=connection)
    await async_session.begin_nested()

    app.dependency_overrides[get_session] = lambda: async_session

    yield async_session

    await async_session.close()
    await transaction.rollback()
    await connection.close()
    drop_database(settings.database_sync + db_id)


@pytest_asyncio.fixture
async def client():
    """
    Получение асинхронного клиента для осуществления запросов.
    :return:
    """

    yield AsyncClient(app=app, base_url=settings.base_url)


@pytest_asyncio.fixture
async def non_mocked_hosts():
    """
    Исключение запросов к приложению из процесса создания мок-объектов для запросов.
    Используется автоматически pytest_httpx.
    https://colin-b.github.io/pytest_httpx/
    :return:
    """

    yield ["localhost", "127.0.0.1", "0.0.0.0"]


@pytest_asyncio.fixture
async def event_producer_publish(mocker: MockerFixture):
    """
    Создание "заглушки" для метода EventProducer.publish().
    :param mocker: MockerFixture
    :return:
    """

    mocker.patch(
        "integrations.events.producer.EventProducer.publish", return_value=None
    )
