from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import asyncio
import asyncpg

load_dotenv()

class Settings(BaseSettings):
    DB_HOST: str = 'db'
    DB_PORT: str = os.getenv('DB_PORT')
    DB_USER: str = os.getenv('DB_USER')
    DB_PASS: str = os.getenv('DB_PASS')
    DB_NAME: str = os.getenv('DB_NAME')

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"



settings = Settings()

async def connect_create_if_not_exists(user, database, password, host, port=5432):
    for i in range(5):
        try:
            conn = await asyncpg.connect(
                user=user, database=database,
                password=password, host=host, port=port
            )
            await conn.close()
            break
        except asyncpg.InvalidCatalogNameError:
            # Database does not exist, create it.
            sys_conn = await asyncpg.connect(
                database='template1',
                user='postgres',
                password=password,
                host=host
            )
            await sys_conn.execute(
                f'CREATE DATABASE "{database}" OWNER "{user}"'
            )
            await sys_conn.close()
            break
        except Exception as e:
            print(e)
            print('Retry in 5 seconds...')
            await asyncio.sleep(5)


def run_init_db():
    asyncio.run(
        connect_create_if_not_exists(
            settings.DB_USER,
            settings.DB_NAME,
            settings.DB_PASS,
            settings.DB_HOST,
            settings.DB_PORT
        )
    )