def test_issue_8():
    """umysqldb.converters should be available since Django 1.6 requires them."""
    from umysqldb.converters import conversions, Thing2Literal
