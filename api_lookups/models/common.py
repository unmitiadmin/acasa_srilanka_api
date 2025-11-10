from settings.database import Base
from typing import List, Optional, TYPE_CHECKING
from typing import Optional
from sqlalchemy import DateTime, ForeignKeyConstraint, Index, Integer, String, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

if TYPE_CHECKING:
    from .analytics import LkpAnalyticsParam

class LkpAnalysisScope(Base):
    __tablename__ = 'lkp_analysis_scope'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scope: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class LkpVisualizationScale(Base):
    __tablename__ = 'lkp_visualization_scale'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scale: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class LkpCommodityType(Base):
    __tablename__ = 'lkp_commodity_type'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    # relations
    lkp_commodity: Mapped[List['LkpCommodity']] = relationship('LkpCommodity', back_populates='type')


class LkpCommodity(Base):
    __tablename__ = 'lkp_commodity'
    __table_args__ = (
        ForeignKeyConstraint(['analytics_param_id'], ['lkp_analytics_param.id'], name='lkp_commodity_ibfk_2'),
        ForeignKeyConstraint(['type_id'], ['lkp_commodity_type.id'], name='lkp_commodity_ibfk_1'),
        Index('analytics_param_id', 'analytics_param_id'),
        Index('type_id', 'type_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(Integer)
    commodity: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    commodity_group: Mapped[Optional[str]] = mapped_column(String(64))
    description: Mapped[Optional[str]] = mapped_column(Text)
    analytics_param_id: Mapped[Optional[int]] = mapped_column(Integer)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    analytics_param: Mapped[Optional['LkpAnalyticsParam']] = relationship('LkpAnalyticsParam', back_populates='lkp_commodity')
    type: Mapped['LkpCommodityType'] = relationship('LkpCommodityType', back_populates='lkp_commodity')


class LkpDataSource(Base):
    __tablename__ = 'lkp_data_source'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class LkpClimateScenario(Base):
    __tablename__ = 'lkp_climate_scenario'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class LkpIntensityMetric(Base):
    __tablename__ = 'lkp_intensity_metric'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric: Mapped[str] = mapped_column(String(32))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class LkpChangeMetric(Base):
    __tablename__ = 'lkp_change_metric'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric: Mapped[str] = mapped_column(String(32))
    p: Mapped[Optional[str]] = mapped_column(String(32))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
