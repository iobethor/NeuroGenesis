from neurogenesis.memory import SemanticMemory


def test_query_orders_by_similarity() -> None:
    mem = SemanticMemory()
    a = mem.add("кошка пьёт молоко")
    b = mem.add("собака любит косточку")
    c = mem.add("молоко и кошка рядом")

    results = mem.query("кошка молоко", top_k=3)
    ids = [item.id for _, item in results]

    assert a.id in ids
    assert c.id in ids
    assert b.id in ids

    # top-2 should be the ones mentioning both query words more strongly
    assert ids[0] in {a.id, c.id}
    assert ids[1] in {a.id, c.id}
    assert ids[0] != ids[1]
