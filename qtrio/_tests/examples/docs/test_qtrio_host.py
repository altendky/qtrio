import qtrio


@qtrio.host
async def test_no_parentheses(request):
    assert True


@qtrio.host()
async def test_just_parentheses(request):
    assert True


@qtrio.host(timeout=20)
async def test_a_keyword_argument(request):
    assert True
