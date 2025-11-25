from __future__ import annotations
from pathlib import Path
from datetime import datetime
import shutil
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "document_taxonomy.yml"
APPLICATIONS_ROOT = ROOT / "Applications"

class DocumentWorkflow:
    def __init__(self, config_path: Path = CONFIG):
        with open(config_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)
        self.base = ROOT / self.cfg.get("root", "Applications")

    def _fmt(self, template: str, company: str, role: str) -> str:
        return template.format(
            year=datetime.now().strftime("%Y"),
            company=company,
            role=role
        )

    def ensure_structure(self, company: str, role: str) -> Path:
        """Create folder structure for an application and return the root path."""
        app_root = self.base / self._fmt("{year}/{company} - {role}", company, role)
        for section in self.cfg.get("schema", []):
            path = self._fmt(section["path"], company, role)
            (self.base / path).mkdir(parents=True, exist_ok=True)
        return app_root

    def route_file(self, src: Path, doc_type: str, company: str, role: str) -> Path:
        """Copy a file into the appropriate taxonomy location based on doc_type."""
        mapping = {
            "job_description": "{year}/{company} - {role}/00_Incoming",
            "resume": "{year}/{company} - {role}/10_Materials",
            "cover_letter": "{year}/{company} - {role}/10_Materials",
            "portfolio": "{year}/{company} - {role}/10_Materials",
            "email": "{year}/{company} - {role}/20_Communications",
            "notes": "{year}/{company} - {role}/20_Communications",
        }
        dest_dir = self.base / self._fmt(mapping.get(doc_type, "{year}/{company} - {role}/00_Incoming"), company, role)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        if src.resolve() != dest.resolve():
            try:
                shutil.copy2(src, dest)
            except FileNotFoundError:
                pass
        return dest

    def get_checklist(self) -> list[dict]:
        return self.cfg.get("checklist", [])

    def compute_incomplete(self, context: dict) -> list[str]:
        """Compute incomplete checklist items from provided context flags."""
        missing = []
        for item in self.get_checklist():
            key = item["id"]
            if not context.get(key):
                missing.append(item["label"])
        return missing

if __name__ == "__main__":
    wf = DocumentWorkflow()
    root = wf.ensure_structure("Acme Corp", "Senior Engineer")
    print(f"Created: {root}")
