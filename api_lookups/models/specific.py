from settings.database import Base
from typing import List, Optional, TYPE_CHECKING
from typing import Optional
from sqlalchemy import DateTime, ForeignKeyConstraint, Index, Integer, String, Text, text, JSON
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
from .common import LkpCommodity, LkpCommodityType

if TYPE_CHECKING:
    from .analytics import LkpAnalyticsParam


class LkpRiskIpcc(Base):
    __tablename__ = 'lkp_risk_ipcc'
    __table_args__ = (
        Index('ipcc', 'ipcc', unique=True),
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ipcc: Mapped[str] = mapped_column(String(32))
    c_label_sufx: Mapped[int] = mapped_column(TINYINT, server_default=text("'0'"))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    c_label_info: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

class LkpRisk(Base):
    __tablename__ = 'lkp_risk'
    __table_args__ = (
        ForeignKeyConstraint(['analytics_param_id'], ['lkp_analytics_param.id'], name='lkp_risk_ibfk_4'),
        ForeignKeyConstraint(['commodity_id'], ['lkp_commodity.id'], name='lkp_risk_ibfk_3'),
        ForeignKeyConstraint(['commodity_type_id'], ['lkp_commodity_type.id'], name='lkp_risk_ibfk_2'),
        ForeignKeyConstraint(['ipcc_id'], ['lkp_risk_ipcc.id'], name='lkp_risk_ibfk_1'),
        Index('analytics_param_id', 'analytics_param_id'),
        Index('commodity_id', 'commodity_id'),
        Index('commodity_type_id', 'commodity_type_id'),
        Index('ipcc_id', 'ipcc_id')
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ipcc_id: Mapped[int] = mapped_column(Integer)
    risk: Mapped[str] = mapped_column(Text)
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    commodity_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    commodity_id: Mapped[Optional[int]] = mapped_column(Integer)
    suffix: Mapped[Optional[str]] = mapped_column(Text)
    hazard_optcode: Mapped[Optional[str]] = mapped_column(String(32))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    analytics_param_id: Mapped[Optional[int]] = mapped_column(Integer)
    # relations
    commodity: Mapped[Optional['LkpCommodity']] = relationship('LkpCommodity', back_populates='lkp_risk')
    commodity_type: Mapped[Optional['LkpCommodityType']] = relationship('LkpCommodityType', back_populates='lkp_risk')
    ipcc: Mapped['LkpRiskIpcc'] = relationship('LkpRiskIpcc', back_populates='lkp_risk')
    analytics_param: Mapped[Optional['LkpAnalyticsParam']] = relationship('LkpAnalyticsParam', back_populates='lkp_risk')


class LkpRiskColor(Base):
    __tablename__ = 'lkp_risk_color'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suffix: Mapped[str] = mapped_column(Text)
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    ramp: Mapped[Optional[dict]] = mapped_column(JSON)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

class LkpRiskCommoditySeason(Base):
    __tablename__ = 'lkp_risk_commodity_season'
    __table_args__ = (
        ForeignKeyConstraint(['commodity_id'], ['lkp_commodity.id'], name='lkp_risk_commodity_season_ibfk_1'),
        Index('commodity_id', 'commodity_id')
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    commodity_id: Mapped[int] = mapped_column(Integer)
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    season: Mapped[Optional[str]] = mapped_column(String(32))
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    # relations
    commodity: Mapped['LkpCommodity'] = relationship('LkpCommodity', back_populates='lkp_risk_commodity_season')


class LkpImpact(Base):
    __tablename__ = 'lkp_impact'
    __table_args__ = (
        ForeignKeyConstraint(['analytics_param_id'], ['lkp_analytics_param.id'], name='lkp_impact_ibfk_1'),
        Index('analytics_param_id', 'analytics_param_id')
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    impact: Mapped[str] = mapped_column(Text)
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    optcode: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    analytics_param_id: Mapped[Optional[int]] = mapped_column(Integer)
    # relations
    analytics_param: Mapped[Optional['LkpAnalyticsParam']] = relationship('LkpAnalyticsParam', back_populates='lkp_impact')


class LkpImpactColor(Base):
    __tablename__ = 'lkp_impact_color'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    suffix: Mapped[Optional[str]] = mapped_column(Text)
    ramp: Mapped[Optional[dict]] = mapped_column(JSON)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class LkpAdaptGroup(Base):
    __tablename__ = 'lkp_adapt_group'
    __table_args__ = (
        ForeignKeyConstraint(['commodity_type_id'], ['lkp_commodity_type.id'], name='lkp_adapt_group_ibfk_1'),
        Index('commodity_type_id', 'commodity_type_id')
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    commodity_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    # relationships
    commodity_type: Mapped[Optional['LkpCommodityType']] = relationship('LkpCommodityType', back_populates='lkp_adapt_group')


class LkpAdaptCropColor(Base):
    __tablename__ = 'lkp_adapt_crop_color'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tab_name: Mapped[str] = mapped_column(String(128))
    prefix: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    ramp: Mapped[Optional[dict]] = mapped_column(JSON)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class LkpAdaptCropOptcode(Base):
    __tablename__ = 'lkp_adapt_crop_optcode'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    optcode: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

class LkpAdaptLivestockColor(Base):
    __tablename__ = 'lkp_adapt_livestock_color'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suffix: Mapped[str] = mapped_column(String(128))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    ramp: Mapped[Optional[dict]] = mapped_column(JSON)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class LkpAdapt(Base):
    __tablename__ = 'lkp_adapt'
    __table_args__ = (
        ForeignKeyConstraint(['analytics_param_id'], ['lkp_analytics_param.id'], name='lkp_adapt_ibfk_4'),
        ForeignKeyConstraint(['commodity_id'], ['lkp_commodity.id'], name='lkp_adapt_ibfk_3'),
        ForeignKeyConstraint(['commodity_type_id'], ['lkp_commodity_type.id'], name='lkp_adapt_ibfk_2'),
        ForeignKeyConstraint(['group_id'], ['lkp_adapt_group.id'], name='lkp_adapt_ibfk_1'),
        Index('analytics_param_id', 'analytics_param_id'),
        Index('commodity_id', 'commodity_id'),
        Index('commodity_type_id', 'commodity_type_id'),
        Index('group_id', 'group_id')
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adaptation: Mapped[str] = mapped_column(Text)
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    group_id: Mapped[Optional[int]] = mapped_column(Integer)
    commodity_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    commodity_id: Mapped[Optional[int]] = mapped_column(Integer)
    optcode: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    analytics_param_id: Mapped[Optional[int]] = mapped_column(Integer)
    # relationships
    commodity: Mapped[Optional['LkpCommodity']] = relationship('LkpCommodity', back_populates='lkp_adapt')
    commodity_type: Mapped[Optional['LkpCommodityType']] = relationship('LkpCommodityType', back_populates='lkp_adapt')
    group: Mapped[Optional['LkpAdaptGroup']] = relationship('LkpAdaptGroup', back_populates='lkp_adapt')
    analytics_param: Mapped[Optional['LkpAnalyticsParam']] = relationship('LkpAnalyticsParam', back_populates='lkp_adapt')


# Parent class relationships - referred by foreign keys
LkpCommodity.lkp_risk = relationship('LkpRisk', back_populates='commodity', lazy='selectin')
LkpCommodity.lkp_adapt = relationship('LkpAdapt', back_populates='commodity', lazy='selectin')
LkpCommodityType.lkp_risk = relationship('LkpRisk', back_populates='commodity_type', lazy='selectin')
LkpCommodityType.lkp_adapt_group = relationship('LkpAdaptGroup', back_populates='commodity_type', lazy='selectin')
LkpCommodityType.lkp_adapt = relationship('LkpAdapt', back_populates='commodity_type', lazy='selectin')
LkpRiskIpcc.lkp_risk = relationship('LkpRisk', back_populates='ipcc', lazy='selectin')
LkpCommodity.lkp_risk_commodity_season = relationship('LkpRiskCommoditySeason', back_populates='commodity', lazy='selectin')
LkpAdaptGroup.lkp_adapt = relationship('LkpAdapt', back_populates='group', lazy='selectin')
