"""
执行记录模型
============
记录每次测试用例的执行结果
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ExecBatch(Base):
    """
    执行批次表

    每次批量执行创建一个批次，关联多条执行记录
    """
    __tablename__ = "exec_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), default="", comment="批次名称")
    status = Column(String(20), default="pending",
                    comment="状态: pending/running/completed/failed")

    # ===== 统计 =====
    total = Column(Integer, default=0, comment="总用例数")
    passed = Column(Integer, default=0, comment="通过数")
    failed = Column(Integer, default=0, comment="失败数")
    errors = Column(Integer, default=0, comment="错误数")

    # ===== 时间 =====
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

    triggered_by = Column(String(50), default="", comment="触发人")

    # 关系
    executions = relationship("Execution", back_populates="batch", lazy="dynamic")

    def to_dict(self):
        total = self.total or 0
        passed = self.passed or 0
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "total": total,
            "passed": passed,
            "failed": self.failed or 0,
            "errors": self.errors or 0,
            "pass_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%",
            "started_at": str(self.started_at) if self.started_at else None,
            "finished_at": str(self.finished_at) if self.finished_at else None,
            "triggered_by": self.triggered_by,
        }


class Execution(Base):
    """
    单条执行记录表

    记录一条测试用例的一次执行结果
    """
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("exec_batches.id"), nullable=True, comment="批次ID")
    case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False, comment="用例ID")
    api_id = Column(Integer, ForeignKey("api_infos.id"), nullable=False, comment="接口ID")

    # ===== 结果 =====
    status = Column(String(20), nullable=False,
                    comment="结果: passed/failed/error/skipped")

    # ===== 请求/响应快照 =====
    request_snapshot = Column(JSON, default=dict, comment="实际发送的请求")
    response_snapshot = Column(JSON, default=dict, comment="实际收到的响应")

    # ===== 断言详情 =====
    assertions = Column(JSON, default=list, comment="断言结果列表")
    error_message = Column(Text, default="", comment="错误信息")

    # ===== 性能数据 =====
    response_time = Column(Integer, default=0, comment="响应时间(ms)")

    executed_at = Column(DateTime, server_default=func.now())

    # ===== 关系 =====
    batch = relationship("ExecBatch", back_populates="executions")
    test_case = relationship("TestCase", back_populates="executions")

    def to_dict(self):
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "case_id": self.case_id,
            "api_id": self.api_id,
            "status": self.status,
            "request_snapshot": self.request_snapshot,
            "response_snapshot": self.response_snapshot,
            "assertions": self.assertions,
            "error_message": self.error_message,
            "response_time": self.response_time,
            "executed_at": str(self.executed_at) if self.executed_at else None,
        }

