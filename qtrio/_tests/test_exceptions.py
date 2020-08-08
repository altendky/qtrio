import qtrio


def test_return_code_error_equality():
    assert qtrio.ReturnCodeError(1) == qtrio.ReturnCodeError(1)


def test_return_code_error_inequality():
    assert qtrio.ReturnCodeError(1) != qtrio.ReturnCodeError(2)
