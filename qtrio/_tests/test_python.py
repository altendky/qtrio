import qtrio._python


def test_identifier_path():
    assert (
        qtrio._python.identifier_path(qtrio._python.identifier_path)
        == "__qtrio__python_identifier_path"
    )
