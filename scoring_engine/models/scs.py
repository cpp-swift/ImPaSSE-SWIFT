import ranking

from copy import copy
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, desc, func
from sqlalchemy.orm import relationship

from scoring_engine.models.base import Base
from scoring_engine.models.check import Check
from scoring_engine.db import session


class SCS(Base):
    __tablename__ = "scs"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="scs", lazy="joined")
    check_name = Column(String(100), nullable=False)
    checks = relationship("Check", back_populates="scs")
    points = Column(Integer, default=100)
    hostname = Column(String(50), nullable=False)
    host = Column(String(50), nullable=False)
    port = Column(Integer, default=0)
    correct = Column(Boolean, default=False)
    accounts = relationship("Account", back_populates="scs")
    environments = relationship("Environment", back_populates="scs")
    configuration_text = Column(String(150), nullable=False)
    worker_queue = Column(String(50), default="main")

    def check_result_for_round(self, round_num):
        for check in self.checks:
            if check.round.number == round_num:
                return check.result
        return False

    def last_check_result(self):
        if not self.checks:
            return None
        return self.checks[-1].result

    @property
    def checks_reversed(self):
        return (
            session.query(Check)
            .filter(Check.service_id == self.id)
            .order_by(desc(Check.round_id))
            .all()
        )
   
