"""
Leistungsverzeichnis model (performance directory / work items)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class LeistungsverzeichnisEntry(Base):
    """Leistungsverzeichnis entry model - work items/positions for a baustelle"""

    __tablename__ = "leistungsverzeichnis_entries"

    id = Column(Integer, primary_key=True, index=True)
    baustelle_id = Column(Integer, ForeignKey("baustellen.id", ondelete="CASCADE"), nullable=False, index=True)
    position_number = Column(String(50))  # e.g., "1.1", "2.3.4"
    description = Column(Text, nullable=False)
    unit = Column(String(50))  # e.g., "m²", "Stk", "Std"
    is_freitext = Column(Boolean, default=False, nullable=False)  # Special "Freitext" entry
    active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    baustelle = relationship("Baustelle", back_populates="lv_entries")
    worktimes = relationship("Worktime", back_populates="lv_entry")

    def __repr__(self):
        return f"<LVEntry(id={self.id}, position='{self.position_number}', baustelle_id={self.baustelle_id})>"
