from app.review import review_code

def test_review_flags_eval_and_debug_output():
    result = review_code("python", "print(eval(input()))")
    rules = {item["rule"] for item in result["findings"]}
    assert "eval-usage" in rules
    assert "debug-print" in rules
    assert result["score"] < 100

def test_review_clean_code_has_no_findings():
    result = review_code("python", "def add(a, b):\n    return a + b\n")
    assert result["findings"] == []
    assert result["score"] == 100
