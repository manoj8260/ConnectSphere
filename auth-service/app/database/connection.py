from sqlmodel import SQLModel ,text
from sqlalchemy.ext.asyncio import AsyncEngine ,create_async_engine ,async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import Config

async_engine :AsyncEngine = create_async_engine(
    url=Config.DATABASE_URL,
    echo =True
)
async def init_db():
    async with async_engine.begin() as conn:
        from app.models.user_model import User
        await conn.run_sync(SQLModel.metadata.create_all)
        # statement = text("SELECT 'hello' ;")
        
        # result  = await conn.execute(statement)
        # print(result.fetchall())

AsyncSessionLocal =  async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit= False
    )
async def get_session():
    async with  AsyncSessionLocal() as session:
        yield session