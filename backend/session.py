"""Single-session state: the model being built, its design log, and the
current print job. One global Session for the hackathon demo (one maker,
one conversation at a time) -- no multi-user session management needed.
"""
from backend.cad.model import Model
from backend.llm.design_log import DesignLog
from backend.slicer.printer import get_printer


class Session:
    def __init__(self):
        self.model = Model()
        self.design_log = DesignLog()
        self.printer = get_printer()
        self.print_job_id: str | None = None
        self.print_settings: dict = {}
