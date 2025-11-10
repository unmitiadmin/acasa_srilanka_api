from settings.database import Base
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKeyConstraint, Index, Integer, String, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime


class LkpCountry(Base):
    __tablename__ = 'lkp_country'
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    iso_code: Mapped[str] = mapped_column(String(2))
    country: Mapped[str] = mapped_column(String(64))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    # relations
    lkp_state: Mapped[List['LkpState']] = relationship('LkpState', back_populates='country')
    lkp_district: Mapped[List['LkpDistrict']] = relationship('LkpDistrict', back_populates='country')


class LkpState(Base):
    __tablename__ = 'lkp_state'
    __table_args__ = (
        ForeignKeyConstraint(['country_id'], ['lkp_country.id'], name='lkp_state_ibfk_1'),
        Index('country_id', 'country_id')
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String(64))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    # erlations
    country: Mapped['LkpCountry'] = relationship('LkpCountry', back_populates='lkp_state')
    lkp_district: Mapped[List['LkpDistrict']] = relationship('LkpDistrict', back_populates='state')


class LkpDistrict(Base):
    __tablename__ = 'lkp_district'
    __table_args__ = (
        ForeignKeyConstraint(['country_id'], ['lkp_country.id'], name='lkp_district_ibfk_1'),
        ForeignKeyConstraint(['state_id'], ['lkp_state.id'], name='lkp_district_ibfk_2'),
        Index('country_id', 'country_id'),
        Index('state_id', 'state_id')
    )
    # fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[int] = mapped_column(Integer)
    district: Mapped[str] = mapped_column(String(64))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"))
    state_id: Mapped[Optional[int]] = mapped_column(Integer)
    updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    # relations
    country: Mapped['LkpCountry'] = relationship('LkpCountry', back_populates='lkp_district')
    state: Mapped[Optional['LkpState']] = relationship('LkpState', back_populates='lkp_district')

    # @property
    # def state_name(self) -> Optional[str]:
    #     return self.state.state if self.state else None
