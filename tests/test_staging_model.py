"""
Test Checkpoint: First Staging Model

Validates first staging model creation.
Tests run in challenge directory, checking jaffle_shop_dbt/models/staging/stg_customers.sql.

Tests check:
- models/staging/ directory exists
- stg_customers.sql exists
- Uses {{ source() }} macro correctly
- Has required column transformations
"""

import pytest
from pathlib import Path


@pytest.fixture
def project_dir():
    """Get jaffle_shop_dbt directory within challenge repo."""
    challenge_dir = Path(__file__).parent.parent
    dbt_project_dir = challenge_dir / "jaffle_shop_dbt"

    assert dbt_project_dir.exists(), (
        f"❌ jaffle_shop_dbt/ directory not found in {challenge_dir}\n"
        f"   Did you copy your dbt project from the previous challenge? (Section 0)\n"
        f"   Run: cp -rP ../PREVIOUS-CHALLENGE/jaffle_shop_dbt ."
    )

    return dbt_project_dir


class TestStagingDirectory:
    """Test staging directory exists (Section 2.1)."""

    def test_staging_directory_exists(self, project_dir):
        """models/staging/ directory must exist."""
        staging_dir = project_dir / "models" / "staging"
        assert staging_dir.exists(), (
            "❌ models/staging/ directory not found\n"
            "   Did you create the staging directory? (Section 2.1)\n"
            "   Run: mkdir -p jaffle_shop_dbt/models/staging"
        )


class TestStagingModel:
    """Test stg_customers.sql staging model (Section 2.1)."""

    def test_stg_customers_exists(self, project_dir):
        """models/staging/stg_customers.sql must exist."""
        model_file = project_dir / "models" / "staging" / "stg_customers.sql"
        assert model_file.exists(), (
            "❌ stg_customers.sql not found in models/staging/\n"
            "   Did you create the file? (Section 2.1)\n"
            "   This is your first transformation model"
        )

    def test_stg_customers_uses_source_macro(self, project_dir):
        """stg_customers.sql must use {{ source() }} macro."""
        model_file = project_dir / "models" / "staging" / "stg_customers.sql"

        if not model_file.exists():
            pytest.skip("stg_customers.sql not found")

        with open(model_file, 'r') as f:
            content = f.read()

        # Check for source macro (with or without spaces)
        has_source_macro = (
            "{{ source(" in content or
            "{{source(" in content or
            "{%- set " in content  # Some templates use set with source
        )

        assert has_source_macro, (
            "❌ stg_customers.sql doesn't use {{ source() }} macro\n"
            "   Section 5.2 required using source macro to reference raw_customers\n"
            "   Example: {{ source('jaffle_shop', 'raw_customers') }}"
        )

    def test_stg_customers_references_jaffle_shop_source(self, project_dir):
        """stg_customers.sql must reference jaffle_shop source."""
        model_file = project_dir / "models" / "staging" / "stg_customers.sql"

        if not model_file.exists():
            pytest.skip("stg_customers.sql not found")

        with open(model_file, 'r') as f:
            content = f.read()

        assert "jaffle_shop" in content, (
            "❌ stg_customers.sql doesn't reference 'jaffle_shop' source\n"
            "   Must use: {{ source('jaffle_shop', 'raw_customers') }}"
        )

    def test_stg_customers_references_raw_customers_table(self, project_dir):
        """stg_customers.sql must reference raw_customers table."""
        model_file = project_dir / "models" / "staging" / "stg_customers.sql"

        if not model_file.exists():
            pytest.skip("stg_customers.sql not found")

        with open(model_file, 'r') as f:
            content = f.read()

        assert "raw_customers" in content, (
            "❌ stg_customers.sql doesn't reference 'raw_customers' table\n"
            "   Must use: {{ source('jaffle_shop', 'raw_customers') }}"
        )

    def test_stg_customers_has_customer_id_column(self, project_dir):
        """stg_customers.sql should rename 'id' to 'customer_id'."""
        model_file = project_dir / "models" / "staging" / "stg_customers.sql"

        if not model_file.exists():
            pytest.skip("stg_customers.sql not found")

        with open(model_file, 'r') as f:
            content = f.read().lower()

        # Check for customer_id in SELECT (case insensitive)
        has_customer_id = "customer_id" in content

        assert has_customer_id, (
            "❌ stg_customers.sql should rename 'id' to 'customer_id'\n"
            "   Section 2.1 requires: id AS customer_id\n"
            "   This makes the column name more descriptive"
        )

    def test_stg_customers_selects_name_columns(self, project_dir):
        """stg_customers.sql should select first_name and last_name."""
        model_file = project_dir / "models" / "staging" / "stg_customers.sql"

        if not model_file.exists():
            pytest.skip("stg_customers.sql not found")

        with open(model_file, 'r') as f:
            content = f.read().lower()

        has_first_name = "first_name" in content
        has_last_name = "last_name" in content

        missing = []
        if not has_first_name:
            missing.append('first_name')
        if not has_last_name:
            missing.append('last_name')

        assert has_first_name and has_last_name, (
            "❌ stg_customers.sql should select first_name and last_name\n"
            "   Section 2.1 requires selecting customer name columns\n"
            f"   Missing: {', '.join(missing)}"
        )

    def test_stg_customers_has_config(self, project_dir):
        """stg_customers.sql should have config for materialization."""
        model_file = project_dir / "models" / "staging" / "stg_customers.sql"

        if not model_file.exists():
            pytest.skip("stg_customers.sql not found")

        with open(model_file, 'r') as f:
            content = f.read()

        # Check for config block (either style)
        has_config = (
            "{{ config(" in content or
            "{{config(" in content or
            "{%- set" in content
        )

        assert has_config, (
            "❌ stg_customers.sql should have {{ config() }} block\n"
            "   Section 2.1 requires: {{ config(materialized='view') }}\n"
            "   This tells dbt how to materialize the model"
        )
