import qtrio._python


def test_identifier_path():
    """Identifier path generation...  works?"""
    assert (
        qtrio._python.identifier_path(qtrio._python.identifier_path)
        == "__qtrio__python_identifier_path"
    )
