import re
from collections import Counter

RULES = [
 ("debug-print", re.compile(r"\b(print|console\.log)\s*\("), "info", "Debug output detected", "Remove temporary debug output or replace it with structured logging."),
 ("bare-except", re.compile(r"except\s*:\s*$", re.M), "high", "Bare exception handler", "Catch specific exception types so failures are not silently hidden."),
 ("hardcoded-secret", re.compile(r"(?i)(api[_-]?key|secret|password)\s*=\s*['\"][^'\"]{6,}['\"]"), "critical", "Possible hardcoded secret", "Move credentials to environment variables or a secret manager."),
 ("eval-usage", re.compile(r"\beval\s*\("), "critical", "Dynamic eval usage", "Avoid evaluating untrusted strings as code."),
 ("todo", re.compile(r"\b(TODO|FIXME)\b"), "info", "Unresolved work marker", "Resolve or track this item before merging."),
]

def review_code(language: str, source: str):
    findings=[]
    lines=source.splitlines()
    for rule, pattern, severity, title, advice in RULES:
        for match in pattern.finditer(source):
            line=source.count("\n",0,match.start())+1
            findings.append({"rule":rule,"severity":severity,"title":title,"line":line,"recommendation":advice})
    complexity_hint=sum(1 for line in lines if re.search(r"\b(if|for|while|try|catch|switch)\b",line))
    duplicate_lines=[line for line,count in Counter(x.strip() for x in lines if x.strip()).items() if count>1 and len(line)>12]
    if complexity_hint>25:
        findings.append({"rule":"complexity-hint","severity":"medium","title":"High control-flow density","line":None,"recommendation":"Consider extracting smaller functions and reducing nested branches."})
    if duplicate_lines:
        findings.append({"rule":"duplicate-lines-hint","severity":"low","title":"Repeated source lines","line":None,"recommendation":"Review repeated statements for opportunities to extract shared logic."})
    weights={"critical":25,"high":12,"medium":6,"low":2,"info":0}
    score=max(0,100-sum(weights[x["severity"]] for x in findings))
    return {"language":language,"score":score,"summary":f"{len(findings)} static review finding(s) detected.","findings":findings,"engine":"ForgeEval deterministic rules v1","disclaimer":"Heuristic static analysis only; this is not an LLM review, compiler, or security certification."}
