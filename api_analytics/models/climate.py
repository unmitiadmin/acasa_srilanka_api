from typing import List, Optional
from settings.database import Base
from sqlalchemy import DateTime, Double, ForeignKeyConstraint, Index, Integer, String, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import decimal
from api_lookups.models import LkpCountry, LkpState, LkpAnalyticsScenario, LkpClimateDataModel


class TblStAnalyticsPrec(Base):
    __tablename__ = 'tbl_st_analytics_prec'
    __table_args__ = (
        ForeignKeyConstraint(['climate_scenario_id'], ['lkp_analytics_scenario.id'], name='tbl_st_analytics_prec_ibfk_4'),
        ForeignKeyConstraint(['country_id'], ['lkp_country.id'], name='tbl_st_analytics_prec_ibfk_1'),
        ForeignKeyConstraint(['data_model_id'], ['lkp_climate_data_model.id'], name='tbl_st_analytics_prec_ibfk_3'),
        ForeignKeyConstraint(['state_id'], ['lkp_state.id'], name='tbl_st_analytics_prec_ibfk_2'),
        Index('climate_scenario_id', 'climate_scenario_id'),
        Index('country_id', 'country_id'),
        Index('data_model_id', 'data_model_id'),
        Index('state_id', 'state_id'),
        Index('year', 'year')
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[Optional[int]] = mapped_column(Integer)
    state_id: Mapped[Optional[int]] = mapped_column(Integer)
    data_model_id: Mapped[Optional[int]] = mapped_column(Integer)
    climate_scenario_id: Mapped[Optional[int]] = mapped_column(Integer)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    value: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    # relationships
    climate_scenario: Mapped[Optional['LkpAnalyticsScenario']] = relationship('LkpAnalyticsScenario', back_populates='tbl_st_analytics_prec')
    country: Mapped[Optional['LkpCountry']] = relationship('LkpCountry', back_populates='tbl_st_analytics_prec')
    data_model: Mapped[Optional['LkpClimateDataModel']] = relationship('LkpClimateDataModel', back_populates='tbl_st_analytics_prec')
    state: Mapped[Optional['LkpState']] = relationship('LkpState', back_populates='tbl_st_analytics_prec')


class TblStAnalyticsTmax(Base):
    __tablename__ = 'tbl_st_analytics_tmax'
    __table_args__ = (
        ForeignKeyConstraint(['climate_scenario_id'], ['lkp_analytics_scenario.id'], name='tbl_st_analytics_tmax_ibfk_4'),
        ForeignKeyConstraint(['country_id'], ['lkp_country.id'], name='tbl_st_analytics_tmax_ibfk_1'),
        ForeignKeyConstraint(['data_model_id'], ['lkp_climate_data_model.id'], name='tbl_st_analytics_tmax_ibfk_3'),
        ForeignKeyConstraint(['state_id'], ['lkp_state.id'], name='tbl_st_analytics_tmax_ibfk_2'),
        Index('climate_scenario_id', 'climate_scenario_id'),
        Index('country_id', 'country_id'),
        Index('data_model_id', 'data_model_id'),
        Index('state_id', 'state_id'),
        Index('year', 'year')
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[Optional[int]] = mapped_column(Integer)
    state_id: Mapped[Optional[int]] = mapped_column(Integer)
    data_model_id: Mapped[Optional[int]] = mapped_column(Integer)
    climate_scenario_id: Mapped[Optional[int]] = mapped_column(Integer)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    value: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    # relationships
    climate_scenario: Mapped[Optional['LkpAnalyticsScenario']] = relationship('LkpAnalyticsScenario', back_populates='tbl_st_analytics_tmax')
    country: Mapped[Optional['LkpCountry']] = relationship('LkpCountry', back_populates='tbl_st_analytics_tmax')
    data_model: Mapped[Optional['LkpClimateDataModel']] = relationship('LkpClimateDataModel', back_populates='tbl_st_analytics_tmax')
    state: Mapped[Optional['LkpState']] = relationship('LkpState', back_populates='tbl_st_analytics_tmax')


class TblStAnalyticsTmin(Base):
    __tablename__ = 'tbl_st_analytics_tmin'
    __table_args__ = (
        ForeignKeyConstraint(['climate_scenario_id'], ['lkp_analytics_scenario.id'], name='tbl_st_analytics_tmin_ibfk_4'),
        ForeignKeyConstraint(['country_id'], ['lkp_country.id'], name='tbl_st_analytics_tmin_ibfk_1'),
        ForeignKeyConstraint(['data_model_id'], ['lkp_climate_data_model.id'], name='tbl_st_analytics_tmin_ibfk_3'),
        ForeignKeyConstraint(['state_id'], ['lkp_state.id'], name='tbl_st_analytics_tmin_ibfk_2'),
        Index('climate_scenario_id', 'climate_scenario_id'),
        Index('country_id', 'country_id'),
        Index('data_model_id', 'data_model_id'),
        Index('state_id', 'state_id'),
        Index('year', 'year')
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[Optional[int]] = mapped_column(Integer)
    state_id: Mapped[Optional[int]] = mapped_column(Integer)
    data_model_id: Mapped[Optional[int]] = mapped_column(Integer)
    climate_scenario_id: Mapped[Optional[int]] = mapped_column(Integer)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    value: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    # relationships
    climate_scenario: Mapped[Optional['LkpAnalyticsScenario']] = relationship('LkpAnalyticsScenario', back_populates='tbl_st_analytics_tmin')
    country: Mapped[Optional['LkpCountry']] = relationship('LkpCountry', back_populates='tbl_st_analytics_tmin')
    data_model: Mapped[Optional['LkpClimateDataModel']] = relationship('LkpClimateDataModel', back_populates='tbl_st_analytics_tmin')
    state: Mapped[Optional['LkpState']] = relationship('LkpState', back_populates='tbl_st_analytics_tmin')


# Parent class relationships - referred by foreign keys
# TblStAnalyticsPrec
LkpCountry.tbl_st_analytics_prec = relationship('TblStAnalyticsPrec', back_populates="country")
LkpState.tbl_st_analytics_prec = relationship('TblStAnalyticsPrec', back_populates="state")
LkpClimateDataModel.tbl_st_analytics_prec = relationship('TblStAnalyticsPrec', back_populates="data_model")
LkpAnalyticsScenario.tbl_st_analytics_prec = relationship('TblStAnalyticsPrec', back_populates="climate_scenario")
# TblStAnalyticsTmax
LkpCountry.tbl_st_analytics_tmax = relationship('TblStAnalyticsTmax', back_populates="country")
LkpState.tbl_st_analytics_tmax = relationship('TblStAnalyticsTmax', back_populates="state")
LkpClimateDataModel.tbl_st_analytics_tmax = relationship('TblStAnalyticsTmax', back_populates="data_model")
LkpAnalyticsScenario.tbl_st_analytics_tmax = relationship('TblStAnalyticsTmax', back_populates="climate_scenario")
# TblStAnalyticsTmin
LkpCountry.tbl_st_analytics_tmin = relationship('TblStAnalyticsTmin', back_populates="country")
LkpState.tbl_st_analytics_tmin = relationship('TblStAnalyticsTmin', back_populates="state")
LkpClimateDataModel.tbl_st_analytics_tmin = relationship('TblStAnalyticsTmin', back_populates="data_model")
LkpAnalyticsScenario.tbl_st_analytics_tmin = relationship('TblStAnalyticsTmin', back_populates="climate_scenario")
