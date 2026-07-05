from app.utils.slug import slugify


def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


def test_slugify_special_chars():
    assert slugify("Hello, World! How are you?") == "hello-world-how-are-you"


def test_slugify_multiple_spaces():
    assert slugify("Hello    World") == "hello-world"


def test_slugify_leading_trailing_spaces():
    assert slugify("  Hello World  ") == "hello-world"


def test_slugify_numbers():
    assert slugify("Mortgage Calculator 2024") == "mortgage-calculator-2024"


def test_slugify_unicode():
    assert slugify("Café Calculator") == "cafe-calculator"


def test_slugify_consecutive_hyphens():
    assert slugify("Hello---World") == "hello-world"
