from app.schemas.common import error_response, paginated_response, success_response


def test_success_response():
    result = success_response(data={"key": "value"}, message="Test")
    assert result["success"] is True
    assert result["message"] == "Test"
    assert result["data"] == {"key": "value"}
    assert result["meta"] is None


def test_success_response_no_data():
    result = success_response(message="No data")
    assert result["success"] is True
    assert result["data"] is None


def test_error_response():
    result = error_response(message="Error occurred", errors=["err1"], code="TEST_ERROR")
    assert result["success"] is False
    assert result["message"] == "Error occurred"
    assert result["errors"] == ["err1"]
    assert result["code"] == "TEST_ERROR"


def test_paginated_response():
    data = [{"id": 1}, {"id": 2}]
    result = paginated_response(data=data, total=10, page=1, per_page=2)
    assert result["success"] is True
    assert len(result["data"]) == 2
    assert result["meta"]["page"] == 1
    assert result["meta"]["total"] == 10
    assert result["meta"]["total_pages"] == 5
    assert result["meta"]["has_next"] is True
    assert result["meta"]["has_prev"] is False


def test_paginated_response_last_page():
    data = [{"id": 1}]
    result = paginated_response(data=data, total=1, page=1, per_page=10)
    assert result["meta"]["has_next"] is False
    assert result["meta"]["has_prev"] is False


def test_error_response_defaults():
    result = error_response()
    assert result["success"] is False
    assert result["message"] == "An error occurred"
    assert result["errors"] == []
    assert result["code"] == "INTERNAL_ERROR"
