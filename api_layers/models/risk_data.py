from typing import Optional
from settings.database import Base
from sqlalchemy import (
    Float, ForeignKeyConstraint, Index, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api_lookups.models import (
    LkpClimateScenario, LkpCommodity, LkpCountry, LkpState, LkpDistrict,
    LkpRiskColor, LkpIntensityMetric, LkpChangeMetric, LkpVisualizationScale,
)

class TblRiskData(Base):
    __tablename__ = 'tbl_risk_data'
    __table_args__ = (
        ForeignKeyConstraint(['change_metric_id'], ['lkp_change_metric.id'], name='tbl_risk_data_ibfk_5'),
        ForeignKeyConstraint(['climate_scenario_id'], ['lkp_climate_scenario.id'], name='tbl_risk_data_ibfk_4'),
        ForeignKeyConstraint(['commodity_id'], ['lkp_commodity.id'], name='tbl_risk_data_ibfk_1'),
        ForeignKeyConstraint(['country_id'], ['lkp_country.id'], name='tbl_risk_data_ibfk_6'),
        ForeignKeyConstraint(['district_id'], ['lkp_district.id'], name='tbl_risk_data_ibfk_9'),
        ForeignKeyConstraint(['intensity_metric_id'], ['lkp_intensity_metric.id'], name='tbl_risk_data_ibfk_2'),
        ForeignKeyConstraint(['risk_suffix_id'], ['lkp_risk_color.id'], name='tbl_risk_data_ibfk_8'),
        ForeignKeyConstraint(['state_id'], ['lkp_state.id'], name='tbl_risk_data_ibfk_7'),
        ForeignKeyConstraint(['visualization_scale_id'], ['lkp_visualization_scale.id'], name='tbl_risk_data_ibfk_3'),
        Index('change_metric_id', 'change_metric_id'),
        Index('climate_scenario_id', 'climate_scenario_id'),
        Index('commodity_id', 'commodity_id'),
        Index('country_id', 'country_id'),
        Index('intensity_metric_id', 'intensity_metric_id'),
        Index('risk_suffix_id', 'risk_suffix_id'),
        Index('state_id', 'state_id'),
        Index('visualization_scale_id', 'visualization_scale_id')
    )
    # fields - foreign keys and indexes
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    commodity_id: Mapped[Optional[int]] = mapped_column(Integer)
    intensity_metric_id: Mapped[Optional[int]] = mapped_column(Integer)
    visualization_scale_id: Mapped[Optional[int]] = mapped_column(Integer)
    climate_scenario_id: Mapped[Optional[int]] = mapped_column(Integer)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    change_metric_id: Mapped[Optional[int]] = mapped_column(Integer)
    country_id: Mapped[Optional[int]] = mapped_column(Integer)
    state_id: Mapped[Optional[int]] = mapped_column(Integer)
    district_id: Mapped[Optional[int]] = mapped_column(Integer)
    risk_suffix_id: Mapped[Optional[int]] = mapped_column(Integer)
    # fields - commodity values
    c_vlow: Mapped[Optional[float]] = mapped_column(Float)
    c_low: Mapped[Optional[float]] = mapped_column(Float)
    c_med: Mapped[Optional[float]] = mapped_column(Float)
    c_high: Mapped[Optional[float]] = mapped_column(Float)
    c_vhigh: Mapped[Optional[float]] = mapped_column(Float)
    c_nil: Mapped[Optional[float]] = mapped_column(Float)
    # fields - population values
    pop_vlow: Mapped[Optional[float]] = mapped_column(Float)
    pop_low: Mapped[Optional[float]] = mapped_column(Float)
    pop_med: Mapped[Optional[float]] = mapped_column(Float)
    pop_high: Mapped[Optional[float]] = mapped_column(Float)
    pop_vhigh: Mapped[Optional[float]] = mapped_column(Float)
    pop_nil: Mapped[Optional[float]] = mapped_column(Float)
    # Forward relationships only
    change_metric: Mapped[Optional['LkpChangeMetric']] = relationship('LkpChangeMetric')
    climate_scenario: Mapped[Optional['LkpClimateScenario']] = relationship('LkpClimateScenario')
    commodity: Mapped[Optional['LkpCommodity']] = relationship('LkpCommodity')
    country: Mapped[Optional['LkpCountry']] = relationship('LkpCountry')
    district: Mapped[Optional['LkpDistrict']] = relationship('LkpDistrict')
    intensity_metric: Mapped[Optional['LkpIntensityMetric']] = relationship('LkpIntensityMetric')
    risk_suffix: Mapped[Optional['LkpRiskColor']] = relationship('LkpRiskColor')
    state: Mapped[Optional['LkpState']] = relationship('LkpState')
    visualization_scale: Mapped[Optional['LkpVisualizationScale']] = relationship('LkpVisualizationScale')
