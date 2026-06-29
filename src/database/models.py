"""
SQLAlchemy ORM models for PostgreSQL
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from config.config import TZ

Base = declarative_base()

class Post(Base):
    """Post model - stores published posts"""
    __tablename__ = "posts"

    id = Column(String(36), primary_key=True)
    facebook_post_id = Column(String(50), unique=True, nullable=True)
    title = Column(String(255), nullable=False)
    hook = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    insight = Column(Text, nullable=True)
    cta = Column(Text, nullable=False)
    hashtags = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    image_alt_text = Column(Text, nullable=True)

    source = Column(String(50), nullable=True)
    source_url = Column(String(500), nullable=True)

    status = Column(String(20), default="pending")
    posted_at = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)

    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    engagement = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)

    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(TZ))
    updated_at = Column(DateTime, default=lambda: datetime.now(TZ))

    def __repr__(self):
        return f"<Post(id={self.id}, status={self.status})>"


class ExecutionLog(Base):
    """Execution log model - tracks agent executions"""
    __tablename__ = "execution_logs"

    id = Column(String(36), primary_key=True)
    agent_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    result_summary = Column(Text, nullable=True)
    execution_id = Column(String(100), nullable=False, unique=True)
    error_message = Column(Text, nullable=True)

    executed_at = Column(DateTime, default=lambda: datetime.now(TZ))
    created_at = Column(DateTime, default=lambda: datetime.now(TZ))

    def __repr__(self):
        return f"<ExecutionLog(agent={self.agent_name}, status={self.status})>"


class Article(Base):
    """Article model - stores scraped articles"""
    __tablename__ = "articles"

    id = Column(String(36), primary_key=True)
    source = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    summary = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)

    views = Column(Integer, default=0)
    stars = Column(Integer, default=0)
    comments = Column(Integer, default=0)

    tags = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)

    verified = Column(Integer, default=0)
    fact_check_score = Column(Float, nullable=True)

    selected_for_post = Column(Integer, default=0)
    selection_score = Column(Float, nullable=True)

    scraped_at = Column(DateTime, default=lambda: datetime.now(TZ))
    created_at = Column(DateTime, default=lambda: datetime.now(TZ))

    def __repr__(self):
        return f"<Article(title={self.title}, source={self.source})>"


class AgentConfig(Base):
    """Agent configuration model"""
    __tablename__ = "agent_configs"

    id = Column(String(36), primary_key=True)
    agent_name = Column(String(100), nullable=False, unique=True)
    role = Column(String(255), nullable=False)
    goal = Column(Text, nullable=False)
    backstory = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=False)
    model = Column(String(50), default="gpt-4-turbo")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)

    enabled = Column(Integer, default=1)

    created_at = Column(DateTime, default=lambda: datetime.now(TZ))
    updated_at = Column(DateTime, default=lambda: datetime.now(TZ))

    def __repr__(self):
        return f"<AgentConfig(agent={self.agent_name})>"
