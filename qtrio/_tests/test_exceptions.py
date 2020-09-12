import qtrio


def test_return_code_error_equality():
    assert qtrio.ReturnCodeError(1) == qtrio.ReturnCodeError(1)


def test_return_code_error_inequality_by_value():
    assert qtrio.ReturnCodeError(1) != qtrio.ReturnCodeError(2)


def test_return_code_error_inequality_by_type():
    assert qtrio.ReturnCodeError(1) != Exception()
