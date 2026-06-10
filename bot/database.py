import asyncio
import aiosqlite
from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, Float, Text, DateTime, JSON, ForeignKey
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from bot.config import load_config

Base = declarative_base()

config = load_config()

# Асинхронный движок SQLite
engine = create_async_engine(config.database_url, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# МОДЕЛИ ТАБЛИЦ
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    
    # Геймификация
    total_xp = Column(Integer, default=0)
    current_rank = Column(String, default="🥚 Новичок")
    badges = Column(JSON, default=list)
    
    # Статистика
    tests_taken = Column(Integer, default=0)
    tests_perfect = Column(Integer, default=0)
    chat_questions = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Прогресс вводного обучения
    intro_welcome_completed = Column(Boolean, default=False)
    intro_product_completed = Column(Boolean, default=False)
    intro_client_completed = Column(Boolean, default=False)
    intro_bitrix_completed = Column(Boolean, default=False)
    intro_final_completed = Column(Boolean, default=False)
    
    # Связи
    test_results = relationship("TestResult", back_populates="user")
    user_badges = relationship("UserBadge", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")

class TestResult(Base):
    __tablename__ = 'test_results'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    section = Column(String)  # 'intro_product', 'intro_client', 'intro_final'
    score = Column(Float)
    max_score = Column(Float)
    feedback = Column(Text)
    passed = Column(Boolean)
    attempt = Column(Integer)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Связь
    user = relationship("User", back_populates="test_results")

class Badge(Base):
    __tablename__ = 'badges'
    
    id = Column(Integer, primary_key=True)
    badge_id = Column(String, unique=True)
    name = Column(String)
    emoji = Column(String)
    description = Column(String)
    xp_reward = Column(Integer)
    is_secret = Column(Boolean, default=False)

class UserBadge(Base):
    __tablename__ = 'user_badges'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    badge_id = Column(String)
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="user_badges")

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Связь
    user = relationship("User", back_populates="chat_history")

async def create_tables():
    """Создает все таблицы в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Получает асинхронную сессию БД"""
    async with async_session() as session:
        yield session

# ФУНКЦИИ ДЛЯ РАБОТЫ С ДАННЫМИ
async def get_or_create_user(telegram_id: int, username: str = None, full_name: str = None):
    """Получает пользователя или создает нового"""
    async with async_session() as session:
        user = await session.get(User, telegram_id)
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                started_at=datetime.utcnow()
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

async def update_user_progress(user_id: int, section: str):
    """Обновляет прогресс по введному обучению"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if section == "intro_welcome":
            user.intro_welcome_completed = True
        elif section == "intro_product":
            user.intro_product_completed = True
        elif section == "intro_client":
            user.intro_client_completed = True
        elif section == "intro_bitrix":
            user.intro_bitrix_completed = True
        elif section == "intro_final":
            user.intro_final_completed = True
            user.completed_at = datetime.utcnow()
        await session.commit()
        return user

async def save_test_result(user_id: int, section: str, score: float, max_score: float, feedback: str, passed: bool, attempt: int):
    """Сохраняет результат теста"""
    async with async_session() as session:
        test_result = TestResult(
            user_id=user_id,
            section=section,
            score=score,
            max_score=max_score,
            feedback=feedback,
            passed=passed,
            attempt=attempt
        )
        session.add(test_result)
        await session.commit()
        return test_result

async def update_user_stats(user_id: int, tests_taken_delta=0, tests_perfect_delta=0, chat_questions_delta=0):
    """Обновляет статистику пользователя"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.tests_taken += tests_taken_delta
        user.tests_perfect += tests_perfect_delta
        user.chat_questions += chat_questions_delta
        await session.commit()
        return user