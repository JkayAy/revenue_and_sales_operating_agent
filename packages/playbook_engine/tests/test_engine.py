from playbook_engine import PlaybookEngine, load_playbook_config


def test_icp_qualified():
    engine = PlaybookEngine(load_playbook_config(None))
    d = engine.evaluate_icp(employee_count=120, country="US", industry="software")
    assert d.allowed
    assert d.code == "icp_qualified"


def test_icp_blocked_industry():
    engine = PlaybookEngine(load_playbook_config(None))
    d = engine.evaluate_icp(employee_count=120, country="US", industry="gambling")
    assert not d.allowed
    assert d.code == "icp_blocked_industry"


def test_citations():
    engine = PlaybookEngine(load_playbook_config(None))
    assert engine.evaluate_citations(sources_count=0).code == "citation_insufficient"
    assert engine.evaluate_citations(sources_count=1).allowed
