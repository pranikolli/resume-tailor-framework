# cli/tailor.py
import argparse
import json
from pathlib import Path
from typing import Optional
from app.models import JobDescription, Evidence, TailorRequest
from app.pipeline import tailor
from dotenv import load_dotenv

load_dotenv()

def run(jd_path: str, master_path: str, out_path: str, target_count: Optional[int] = None) -> str:
    jd = JobDescription(**json.loads(Path(jd_path).read_text()))
    master = [Evidence(**e) for e in json.loads(Path(master_path).read_text())]
    req = TailorRequest(
        jd=jd,
        master_resume_bullets=master,
        target_count=target_count or 6,
    )
    resp = tailor(req)
    Path(out_path).write_text(json.dumps(resp.model_dump(), indent=2))
    return out_path

def main():
    parser = argparse.ArgumentParser(description="Tailor resume bullets from a job description.")
    parser.add_argument("jd", help="Path to job description JSON")
    parser.add_argument("master", help="Path to master resume evidence JSON")
    parser.add_argument("out", help="Path to write output JSON")
    parser.add_argument("--target", type=int, default=None, help="Target number of bullets (default 6)")
    args = parser.parse_args()
    out = run(args.jd, args.master, args.out, args.target)
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
