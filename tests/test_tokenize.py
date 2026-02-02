from neurogenesis.tokenize import bow, tokenize


def test_tokenize_latin_and_cyrillic() -> None:
    tokens = tokenize("Привет, world! Ёжик 123.")
    assert tokens == ["привет", "world", "ёжик", "123"]


def test_bow_counts() -> None:
    assert bow(["a", "b", "a"]) == {"a": 2, "b": 1}
