"""Inspect blocked KDP jobs and resume only after an explicit owner approval."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from typing import Any

RUN_ID_RE=re.compile(r"(?im)^\s*Workflow run ID:\s*(\d+)\s*$")
ALLOWED_WORKFLOWS={"KDP Production Pipeline","Inspector Tests"}

def approved_run_ids(issues: list[dict[str,Any]]) -> list[tuple[int,int]]:
    approved=[]
    for issue in issues:
        labels={label.get("name","") for label in issue.get("labels",[])}
        if not {"human-intervention","approved-to-resume"}.issubset(labels):
            continue
        match=RUN_ID_RE.search(issue.get("body",""))
        if match:
            approved.append((int(issue["number"]),int(match.group(1))))
    return approved

def validate_manual_resume(run_id: str, approval_note: str) -> str|None:
    if not run_id.isdigit():
        return "manual resume requires a numeric GitHub Actions run ID"
    if len(approval_note.strip())<12:
        return "manual resume requires an explicit owner approval note (at least 12 characters)"
    return None

def validate_run_target(run_info: dict[str,Any]) -> str|None:
    workflow=run_info.get("workflowName") or run_info.get("name")
    if workflow not in ALLOWED_WORKFLOWS:
        return "run is not from an approved KDP workflow"
    if run_info.get("status")!="completed" or run_info.get("conclusion")!="failure":
        return "only completed failed workflow runs can be resumed"
    if run_info.get("headBranch")!="main":
        return "only failed runs from the trusted main branch can be resumed"
    return None

def _gh(args: list[str], capture: bool=True) -> str:
    result=subprocess.run(["gh",*args],check=True,text=True,capture_output=capture)
    return result.stdout if capture else ""

def _run_info(repo: str, run_id: int) -> dict[str,Any]:
    raw=_gh(["run","view",str(run_id),"--repo",repo,"--json","name,status,conclusion,headBranch"])
    return json.loads(raw)

def inspect(repo: str) -> dict[str,Any]:
    raw=_gh(["run","list","--repo",repo,"--workflow","KDP Production Pipeline","--limit","10","--json","databaseId,name,status,conclusion,headBranch,url"])
    return {"action":"inspect","runs":json.loads(raw)}

def poll_and_resume(repo: str) -> dict[str,Any]:
    raw=_gh(["issue","list","--repo",repo,"--state","open","--label","human-intervention","--json","number,title,body,labels","--limit","50"])
    issues=json.loads(raw)
    resumed=[]
    skipped=[]
    approved=approved_run_ids(issues)
    for issue_number,run_id in approved:
        try:
            reason=validate_run_target(_run_info(repo,run_id))
            if reason:
                skipped.append({"issue":issue_number,"run_id":run_id,"reason":reason})
                continue
            _gh(["run","rerun",str(run_id),"--failed","--repo",repo],capture=False)
            _gh(["issue","edit",str(issue_number),"--repo",repo,"--add-label","resume-started","--remove-label","approved-to-resume"],capture=False)
            resumed.append({"issue":issue_number,"run_id":run_id,"status":"rerun_requested"})
        except (subprocess.CalledProcessError,json.JSONDecodeError) as exc:
            skipped.append({"issue":issue_number,"run_id":run_id,"reason":str(exc)})
    return {"action":"scheduled_poll","approved_count":len(approved),"resumed":resumed,"skipped":skipped}

def manual_resume(repo: str, run_id: str, approval_note: str) -> dict[str,Any]:
    error=validate_manual_resume(run_id,approval_note)
    if error:
        raise ValueError(error)
    run_info=_run_info(repo,int(run_id))
    target_error=validate_run_target(run_info)
    if target_error:
        raise ValueError(target_error)
    _gh(["run","rerun",run_id,"--failed","--repo",repo],capture=False)
    return {"action":"manual_resume","run_id":int(run_id),"status":"rerun_requested","approval_note_recorded":True}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",required=True)
    parser.add_argument("--action",choices=["inspect","resume-approved"],default="inspect")
    parser.add_argument("--event",choices=["workflow_dispatch","schedule"],default="workflow_dispatch")
    parser.add_argument("--run-id",default="")
    parser.add_argument("--approval-note",default="")
    args=parser.parse_args()
    try:
        if args.event=="schedule":
            result=poll_and_resume(args.repo)
        elif args.action=="resume-approved":
            result=manual_resume(args.repo,args.run_id,args.approval_note)
        else:
            result=inspect(args.repo)
    except (ValueError,subprocess.CalledProcessError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"ERROR","error":str(exc)},indent=2),file=sys.stderr)
        return 1
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
