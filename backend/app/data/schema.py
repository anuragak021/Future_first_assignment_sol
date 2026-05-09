# Schema — SQLAlchemy ORM models for the structured data layer
from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    genre = Column(String(100), nullable=False)
    releaseYear = Column("release_year", Integer, nullable=False)
    director = Column(String(255))
    budget = Column(Float)
    duration = Column(Integer)  # minutes

    watchActivities = relationship("WatchActivity", back_populates="movie")
    reviews = relationship("Review", back_populates="movie")
    marketingSpends = relationship("MarketingSpend", back_populates="movie")


class Viewer(Base):
    __tablename__ = "viewers"

    id = Column(Integer, primary_key=True, index=True)
    ageGroup = Column("age_group", String(20), nullable=False)
    gender = Column(String(20))
    region = Column(String(100))
    city = Column(String(100))
    subscriptionTier = Column("subscription_tier", String(50))

    watchActivities = relationship("WatchActivity", back_populates="viewer")
    reviews = relationship("Review", back_populates="viewer")


class WatchActivity(Base):
    __tablename__ = "watch_activity"

    id = Column(Integer, primary_key=True, index=True)
    movieId = Column("movie_id", Integer, ForeignKey("movies.id"), nullable=False)
    viewerId = Column("viewer_id", Integer, ForeignKey("viewers.id"), nullable=False)
    watchDate = Column("watch_date", Date, nullable=False)
    watchMinutes = Column("watch_minutes", Float, nullable=False)
    completionRate = Column("completion_rate", Float, nullable=False)  # 0.0–1.0

    movie = relationship("Movie", back_populates="watchActivities")
    viewer = relationship("Viewer", back_populates="watchActivities")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    movieId = Column("movie_id", Integer, ForeignKey("movies.id"), nullable=False)
    viewerId = Column("viewer_id", Integer, ForeignKey("viewers.id"), nullable=False)
    rating = Column(Float, nullable=False)  # 1.0–5.0
    reviewDate = Column("review_date", Date, nullable=False)
    sentiment = Column(String(20))  # positive/neutral/negative

    movie = relationship("Movie", back_populates="reviews")
    viewer = relationship("Viewer", back_populates="reviews")


class MarketingSpend(Base):
    __tablename__ = "marketing_spend"

    id = Column(Integer, primary_key=True, index=True)
    movieId = Column("movie_id", Integer, ForeignKey("movies.id"), nullable=False)
    channel = Column(String(100), nullable=False)
    spendAmount = Column("spend_amount", Float, nullable=False)
    period = Column(String(20), nullable=False)  # e.g. "2025-Q1"
    impressions = Column(Integer)
    clicks = Column(Integer)

    movie = relationship("Movie", back_populates="marketingSpends")


class RegionalPerformance(Base):
    __tablename__ = "regional_performance"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    movieId = Column("movie_id", Integer, ForeignKey("movies.id"), nullable=True)
    period = Column(String(20), nullable=False)
    totalWatchMinutes = Column("total_watch_minutes", Float)
    uniqueViewers = Column("unique_viewers", Integer)
    avgCompletionRate = Column("avg_completion_rate", Float)
    revenueEstimate = Column("revenue_estimate", Float)
