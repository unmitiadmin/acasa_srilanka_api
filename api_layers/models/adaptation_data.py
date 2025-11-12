from typing import Optional
from settings.database import Base
from sqlalchemy import (
    Float, ForeignKeyConstraint, Index, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api_lookups.models import (
    LkpClimateScenario, LkpCommodity, LkpCountry, LkpState, LkpDistrict,
    LkpAdaptCropColor, LkpAdaptCropOptcode, LkpAdaptLivestockColor,
    LkpIntensityMetric, LkpChangeMetric, LkpVisualizationScale,
)


class TblAdaptCropData(Base):
    __tablename__ = 'tbl_adapt_crop_data'
    __table_args__ = (
        ForeignKeyConstraint(['adaptation_optcode_id'], ['lkp_adapt_crop_optcode.id'], name='tbl_adapt_crop_data_ibfk_9'),
        ForeignKeyConstraint(['adaptation_prefix_id'], ['lkp_adapt_crop_color.id'], name='tbl_adapt_crop_data_ibfk_8'),
        ForeignKeyConstraint(['change_metric_id'], ['lkp_change_metric.id'], name='tbl_adapt_crop_data_ibfk_5'),
        ForeignKeyConstraint(['climate_scenario_id'], ['lkp_climate_scenario.id'], name='tbl_adapt_crop_data_ibfk_4'),
        ForeignKeyConstraint(['commodity_id'], ['lkp_commodity.id'], name='tbl_adapt_crop_data_ibfk_1'),
        ForeignKeyConstraint(['country_id'], ['lkp_country.id'], name='tbl_adapt_crop_data_ibfk_6'),
        ForeignKeyConstraint(['district_id'], ['lkp_district.id'], name='tbl_adapt_crop_data_ibfk_10'),
        ForeignKeyConstraint(['intensity_metric_id'], ['lkp_intensity_metric.id'], name='tbl_adapt_crop_data_ibfk_2'),
        ForeignKeyConstraint(['state_id'], ['lkp_state.id'], name='tbl_adapt_crop_data_ibfk_7'),
        ForeignKeyConstraint(['visualization_scale_id'], ['lkp_visualization_scale.id'], name='tbl_adapt_crop_data_ibfk_3'),
        Index('adaptation_optcode_id', 'adaptation_optcode_id'),
        Index('adaptation_prefix_id', 'adaptation_prefix_id'),
        Index('change_metric_id', 'change_metric_id'),
        Index('climate_scenario_id', 'climate_scenario_id'),
        Index('commodity_id', 'commodity_id'),
        Index('country_id', 'country_id'),
        Index('intensity_metric_id', 'intensity_metric_id'),
        Index('state_id', 'state_id'),
        Index('visualization_scale_id', 'visualization_scale_id'),
        Index('year', 'year')
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
    adaptation_prefix_id: Mapped[Optional[int]] = mapped_column(Integer)
    adaptation_optcode_id: Mapped[Optional[int]] = mapped_column(Integer)
    # fields - commodity values
    c_vlow: Mapped[Optional[float]] = mapped_column(Float)
    c_low: Mapped[Optional[float]] = mapped_column(Float)
    c_med: Mapped[Optional[float]] = mapped_column(Float)
    c_high: Mapped[Optional[float]] = mapped_column(Float)
    c_vhigh: Mapped[Optional[float]] = mapped_column(Float)
    c_uns: Mapped[Optional[float]] = mapped_column(Float)
    c_nil: Mapped[Optional[float]] = mapped_column(Float)
    # fields - population values
    pop_vlow: Mapped[Optional[float]] = mapped_column(Float)
    pop_low: Mapped[Optional[float]] = mapped_column(Float)
    pop_med: Mapped[Optional[float]] = mapped_column(Float)
    pop_high: Mapped[Optional[float]] = mapped_column(Float)
    pop_vhigh: Mapped[Optional[float]] = mapped_column(Float)
    pop_uns: Mapped[Optional[float]] = mapped_column(Float)
    pop_nil: Mapped[Optional[float]] = mapped_column(Float)
    # Forward relationships only - no need of back_populates
    adaptation_optcode: Mapped[Optional['LkpAdaptCropOptcode']] = relationship('LkpAdaptCropOptcode')
    adaptation_prefix: Mapped[Optional['LkpAdaptCropColor']] = relationship('LkpAdaptCropColor')
    change_metric: Mapped[Optional['LkpChangeMetric']] = relationship('LkpChangeMetric')
    climate_scenario: Mapped[Optional['LkpClimateScenario']] = relationship('LkpClimateScenario')
    commodity: Mapped[Optional['LkpCommodity']] = relationship('LkpCommodity')
    country: Mapped[Optional['LkpCountry']] = relationship('LkpCountry')
    district: Mapped[Optional['LkpDistrict']] = relationship('LkpDistrict')
    intensity_metric: Mapped[Optional['LkpIntensityMetric']] = relationship('LkpIntensityMetric')
    state: Mapped[Optional['LkpState']] = relationship('LkpState')
    visualization_scale: Mapped[Optional['LkpVisualizationScale']] = relationship('LkpVisualizationScale')


class TblAdaptLivestockData(Base):
    __tablename__ = 'tbl_adapt_livestock_data'
    __table_args__ = (
        ForeignKeyConstraint(['adaptation_optcode_id'], ['lkp_adapt_livestock_color.id'], name='tbl_adapt_livestock_data_ibfk_8'),
        ForeignKeyConstraint(['change_metric_id'], ['lkp_change_metric.id'], name='tbl_adapt_livestock_data_ibfk_5'),
        ForeignKeyConstraint(['climate_scenario_id'], ['lkp_climate_scenario.id'], name='tbl_adapt_livestock_data_ibfk_4'),
        ForeignKeyConstraint(['commodity_id'], ['lkp_commodity.id'], name='tbl_adapt_livestock_data_ibfk_1'),
        ForeignKeyConstraint(['country_id'], ['lkp_country.id'], name='tbl_adapt_livestock_data_ibfk_6'),
        ForeignKeyConstraint(['district_id'], ['lkp_district.id'], name='tbl_adapt_livestock_data_ibfk_9'),
        ForeignKeyConstraint(['intensity_metric_id'], ['lkp_intensity_metric.id'], name='tbl_adapt_livestock_data_ibfk_2'),
        ForeignKeyConstraint(['state_id'], ['lkp_state.id'], name='tbl_adapt_livestock_data_ibfk_7'),
        ForeignKeyConstraint(['visualization_scale_id'], ['lkp_visualization_scale.id'], name='tbl_adapt_livestock_data_ibfk_3'),
        Index('adaptation_optcode_id', 'adaptation_optcode_id'),
        Index('change_metric_id', 'change_metric_id'),
        Index('climate_scenario_id', 'climate_scenario_id'),
        Index('commodity_id', 'commodity_id'),
        Index('country_id', 'country_id'),
        Index('intensity_metric_id', 'intensity_metric_id'),
        Index('state_id', 'state_id'),
        Index('visualization_scale_id', 'visualization_scale_id'),
        Index('year', 'year')
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
    adaptation_optcode_id: Mapped[Optional[int]] = mapped_column(Integer)
    # fields - commodity values
    c_vlow: Mapped[Optional[float]] = mapped_column(Float)
    c_low: Mapped[Optional[float]] = mapped_column(Float)
    c_med: Mapped[Optional[float]] = mapped_column(Float)
    c_high: Mapped[Optional[float]] = mapped_column(Float)
    c_vhigh: Mapped[Optional[float]] = mapped_column(Float)
    c_uns: Mapped[Optional[float]] = mapped_column(Float)
    c_nil: Mapped[Optional[float]] = mapped_column(Float)
    # fields - population values
    pop_vlow: Mapped[Optional[float]] = mapped_column(Float)
    pop_low: Mapped[Optional[float]] = mapped_column(Float)
    pop_med: Mapped[Optional[float]] = mapped_column(Float)
    pop_high: Mapped[Optional[float]] = mapped_column(Float)
    pop_vhigh: Mapped[Optional[float]] = mapped_column(Float)
    pop_uns: Mapped[Optional[float]] = mapped_column(Float)
    pop_nil: Mapped[Optional[float]] = mapped_column(Float)
    # Forward relationships only - no need of back_populates
    adaptation_optcode: Mapped[Optional['LkpAdaptLivestockColor']] = relationship('LkpAdaptLivestockColor')
    change_metric: Mapped[Optional['LkpChangeMetric']] = relationship('LkpChangeMetric')
    climate_scenario: Mapped[Optional['LkpClimateScenario']] = relationship('LkpClimateScenario')
    commodity: Mapped[Optional['LkpCommodity']] = relationship('LkpCommodity')
    country: Mapped[Optional['LkpCountry']] = relationship('LkpCountry')
    district: Mapped[Optional['LkpDistrict']] = relationship('LkpDistrict')
    intensity_metric: Mapped[Optional['LkpIntensityMetric']] = relationship('LkpIntensityMetric')
    state: Mapped[Optional['LkpState']] = relationship('LkpState')
    visualization_scale: Mapped[Optional['LkpVisualizationScale']] = relationship('LkpVisualizationScale')
