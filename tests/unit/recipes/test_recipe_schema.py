"""Tests for the strict recipe parser."""

import json
from pathlib import PurePosixPath

import pytest
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from django_start.domain.errors import ConfigurationError
from django_start.recipes.parser import parse_recipe_metadata

VALID_JSON = """{
  "recipe_schema_version": "1.0",
  "recipe_version": "2.0.0",
  "name": "standard",
  "description": "Standard Django starter.",
  "python_requires": ">=3.12,<3.15",
  "django_requires": ">=5.2,<6.2",
  "django_start_requires": ">=2.0.0a1,<3",
  "dependencies": ["djangorestframework>=3.18.1,<3.19"],
  "template_dir": "templates"
}"""


def test_parse_valid_recipe():
    metadata = parse_recipe_metadata(VALID_JSON)
    assert metadata.recipe_schema_version == "1.0"
    assert metadata.recipe_version == Version("2.0.0")
    assert metadata.name == "standard"
    assert metadata.description == "Standard Django starter."
    assert metadata.python_requires == SpecifierSet(">=3.12,<3.15")
    assert metadata.django_requires == SpecifierSet(">=5.2,<6.2")
    assert metadata.django_start_requires == SpecifierSet(">=2.0.0a1,<3")
    assert metadata.dependencies == ("djangorestframework>=3.18.1,<3.19",)
    assert metadata.template_dir == PurePosixPath("templates")


def test_invalid_json():
    with pytest.raises(ConfigurationError, match="Invalid recipe JSON"):
        parse_recipe_metadata("{")


def test_missing_field():
    data = json.loads(VALID_JSON)
    del data["name"]
    with pytest.raises(
        ConfigurationError, match="missing required fields: name"
    ):
        parse_recipe_metadata(json.dumps(data))


def test_unknown_field():
    data = json.loads(VALID_JSON)
    data["unknown_xyz"] = "foo"
    with pytest.raises(
        ConfigurationError, match="unknown fields: unknown_xyz"
    ):
        parse_recipe_metadata(json.dumps(data))


def test_forbidden_field():
    data = json.loads(VALID_JSON)
    data["post_generate_hooks"] = ["echo hi"]
    with pytest.raises(
        ConfigurationError, match="forbidden fields: post_generate_hooks"
    ):
        parse_recipe_metadata(json.dumps(data))


def test_invalid_schema_version():
    data = json.loads(VALID_JSON)
    data["recipe_schema_version"] = "1.1"
    with pytest.raises(
        ConfigurationError, match="Unsupported recipe schema version: '1.1'"
    ):
        parse_recipe_metadata(json.dumps(data))


def test_invalid_recipe_version():
    data = json.loads(VALID_JSON)
    data["recipe_version"] = "abc"
    with pytest.raises(ConfigurationError, match="Invalid PEP 440 version"):
        parse_recipe_metadata(json.dumps(data))


def test_invalid_specifier():
    data = json.loads(VALID_JSON)
    data["python_requires"] = ">=3.12.bad"
    with pytest.raises(ConfigurationError, match="Invalid PEP 440 specifier"):
        parse_recipe_metadata(json.dumps(data))


def test_unbounded_dependency():
    data = json.loads(VALID_JSON)
    data["dependencies"] = ["requests>=2.0"]
    with pytest.raises(
        ConfigurationError, match="must have a bounded upper constraint"
    ):
        parse_recipe_metadata(json.dumps(data))


def test_direct_url_dependency():
    data = json.loads(VALID_JSON)
    data["dependencies"] = ["pkg@https://example.com/pkg.zip"]
    with pytest.raises(ConfigurationError, match="must not use a direct URL"):
        parse_recipe_metadata(json.dumps(data))


def test_django_dependency_rejected():
    data = json.loads(VALID_JSON)
    data["dependencies"] = ["Django>=5.2,<6.0"]
    with pytest.raises(ConfigurationError, match="must not declare Django"):
        parse_recipe_metadata(json.dumps(data))


def test_duplicate_dependency():
    data = json.loads(VALID_JSON)
    data["dependencies"] = ["pkg>=1,<2", "Pkg>=1.5,<2"]
    with pytest.raises(ConfigurationError, match="duplicates package"):
        parse_recipe_metadata(json.dumps(data))


def test_absolute_template_dir():
    data = json.loads(VALID_JSON)
    data["template_dir"] = "/templates"
    with pytest.raises(ConfigurationError, match="must be relative"):
        parse_recipe_metadata(json.dumps(data))


def test_traversal_template_dir():
    data = json.loads(VALID_JSON)
    data["template_dir"] = "../templates"
    with pytest.raises(ConfigurationError, match="must not contain '\\.\\.'"):
        parse_recipe_metadata(json.dumps(data))


def test_dependency_bounding():
    data = json.loads(VALID_JSON)
    # foo>=1,!=2 -> rejected
    data["dependencies"] = ["foo>=1,!=2"]
    with pytest.raises(ConfigurationError, match="bounded upper constraint"):
        parse_recipe_metadata(json.dumps(data))

    # foo>=1,<2 -> accepted
    data["dependencies"] = ["foo>=1,<2"]
    parse_recipe_metadata(json.dumps(data))

    # foo~=1.4 -> accepted
    data["dependencies"] = ["foo~=1.4"]
    parse_recipe_metadata(json.dumps(data))

    # foo==1.4.2 -> accepted
    data["dependencies"] = ["foo==1.4.2"]
    parse_recipe_metadata(json.dumps(data))

    # foo>=1 -> rejected
    data["dependencies"] = ["foo>=1"]
    with pytest.raises(ConfigurationError, match="bounded upper constraint"):
        parse_recipe_metadata(json.dumps(data))
