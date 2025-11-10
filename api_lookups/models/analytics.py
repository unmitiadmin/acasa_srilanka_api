from settings.database import Base
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKeyConstraint, Index, Integer, String, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
from .common import LkpCommodity
from .specific import LkpRisk, LkpImpact, LkpAdapt


class LkpAnalyticsScenario(Base):
    __tablename__ = 'lkp_analytics_scenario'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class LkpClimateDataModel(Base):
    __tablename__ = 'lkp_climate_data_model'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model: Mapped[str] = mapped_column(String(32))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class LkpAnalyticsParam(Base):
    __tablename__ = 'lkp_analytics_param'
    # Fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    param: Mapped[str] = mapped_column(Text)
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    units: Mapped[Optional[str]] = mapped_column(String(16))
    table_name: Mapped[Optional[str]] = mapped_column(String(128))
    model: Mapped[Optional[str]] = mapped_column(String(128))
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    # Child relations (backward)
    lkp_commodity: Mapped[list['LkpCommodity']] = relationship('LkpCommodity', back_populates='analytics_param')
    lkp_risk: Mapped[list['LkpRisk']] = relationship('LkpRisk', back_populates='analytics_param')
    lkp_impact: Mapped[list['LkpImpact']] = relationship('LkpImpact', back_populates='analytics_param')
    lkp_adapt: Mapped[list['LkpAdapt']] = relationship('LkpAdapt', back_populates='analytics_param')