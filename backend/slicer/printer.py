"""Printer control: OctoPrint/PrusaLink client. Mock printer if PRINTER_URL
is unset, so print status can be spoken during dev/demo without hardware.
"""
import os
import time


class Printer:
    def upload_and_print(self, gcode_path: str) -> str:
        raise NotImplementedError

    def status(self, job_id: str) -> dict:
        raise NotImplementedError

    def pause(self, job_id: str): ...
    def cancel(self, job_id: str): ...


class OctoPrintPrinter(Printer):
    def __init__(self, url: str, api_key: str):
        self.url = url.rstrip("/")
        self.api_key = api_key

    def upload_and_print(self, gcode_path: str) -> str:
        import requests

        with open(gcode_path, "rb") as f:
            resp = requests.post(
                f"{self.url}/api/files/local",
                headers={"X-Api-Key": self.api_key},
                files={"file": f},
                data={"print": "true"},
                timeout=30,
            )
        resp.raise_for_status()
        return os.path.basename(gcode_path)

    def status(self, job_id: str) -> dict:
        import requests

        resp = requests.get(
            f"{self.url}/api/job", headers={"X-Api-Key": self.api_key}, timeout=10
        )
        resp.raise_for_status()
        return resp.json()

    def pause(self, job_id: str):
        self._send_command("pause")

    def cancel(self, job_id: str):
        self._send_command("cancel")

    def _send_command(self, command: str):
        import requests

        requests.post(
            f"{self.url}/api/job",
            headers={"X-Api-Key": self.api_key},
            json={"command": command},
            timeout=10,
        )


class MockPrinter(Printer):
    """Simulates a print job progressing over time for demo/testing."""

    def __init__(self):
        self._start_time = None
        self._duration_s = 60 * 8  # pretend 8 minute print

    def upload_and_print(self, gcode_path: str) -> str:
        self._start_time = time.time()
        return "mock-job-1"

    def status(self, job_id: str) -> dict:
        if self._start_time is None:
            return {"state": "idle", "progress": 0}
        elapsed = time.time() - self._start_time
        progress = min(100, int(100 * elapsed / self._duration_s))
        state = "printing" if progress < 100 else "done"
        return {"state": state, "progress": progress}

    def pause(self, job_id: str):
        pass

    def cancel(self, job_id: str):
        self._start_time = None


def get_printer() -> Printer:
    url = os.getenv("PRINTER_URL")
    key = os.getenv("PRINTER_API_KEY")
    return OctoPrintPrinter(url, key) if url and key else MockPrinter()
