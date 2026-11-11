"""
Unit Tests for Sovereign Practice Vault Structured Transaction Engine.

Purpose:
  Validates deterministic transaction extraction from email correspondence,
  database persistence, deduplication, SQL aggregations, and markdown table
  formatting.
"""

from pathlib import Path
import pytest
from app.transactions import TransactionRecord, TransactionStore


@pytest.fixture
def temp_store(tmp_path: Path) -> TransactionStore:
    """Provide an isolated temporary TransactionStore instance."""
    db_file = tmp_path / "test_transactions.db"
    return TransactionStore(db_path=db_file)


def test_extract_transaction_from_email(temp_store: TransactionStore) -> None:
    """Test extracting purchase details from receipt correspondence."""
    subject = "Your order #56295196"
    sender = '"Côte Brasserie" <no-reply@pepperhq.com>'
    date_header = "Sat, 7 Nov 2026 15:46:46 +0000"
    text = (
        "Hello Neville, Thanks for visiting Côte Henley. Total paid: £64.74. "
        "Here is your receipt for your order."
    )

    tx = temp_store.extract_from_email(
        chunk_id="gmail#test1#p1#c0",
        subject=subject,
        sender=sender,
        date_header=date_header,
        text=text,
    )

    assert tx is not None
    assert tx.merchant == "Côte Brasserie"
    assert tx.amount_minor == 6474
    assert tx.amount_display == "£64.74"
    assert tx.currency == "GBP"
    assert tx.year == 2026
    assert tx.month == 11
    assert tx.transaction_date == "2026-11-07"


def test_insert_and_deduplicate(temp_store: TransactionStore) -> None:
    """Test that duplicate transactions are safely ignored."""
    tx = TransactionRecord(
        transaction_date="2025-05-12",
        year=2025,
        month=5,
        merchant="Amazon.co.uk",
        item_description="Legal Textbooks",
        amount_minor=4500,
        currency="GBP",
        amount_display="£45.00",
        source_message_id="gmail#tx99#p1#c0",
        subject="Your Amazon.co.uk order",
        confidence=1.0,
    )

    # First insertion should succeed.
    assert temp_store.insert_transaction(tx) is True

    # Duplicate insertion with identical key should be safely ignored.
    assert temp_store.insert_transaction(tx) is False

    res = temp_store.query_transactions()
    assert res["count"] == 1
    assert res["total_display"] == "£45.00"


def test_query_filtering_and_sums(temp_store: TransactionStore) -> None:
    """Test deterministic SQL summation, merchant grouping, and filtering."""
    tx1 = TransactionRecord(
        transaction_date="2025-01-10",
        year=2025,
        month=1,
        merchant="Amazon.co.uk",
        item_description="Office supplies",
        amount_minor=2000,
        currency="GBP",
        amount_display="£20.00",
        source_message_id="gmail#1#p1#c0",
        subject="Order 1",
    )
    tx2 = TransactionRecord(
        transaction_date="2025-06-15",
        year=2025,
        month=6,
        merchant="Amazon.co.uk",
        item_description="External SSD",
        amount_minor=8000,
        currency="GBP",
        amount_display="£80.00",
        source_message_id="gmail#2#p1#c0",
        subject="Order 2",
    )
    tx3 = TransactionRecord(
        transaction_date="2026-02-01",
        year=2026,
        month=2,
        merchant="Apple",
        item_description="Keyboard",
        amount_minor=10000,
        currency="GBP",
        amount_display="£100.00",
        source_message_id="gmail#3#p1#c0",
        subject="Order 3",
    )

    temp_store.insert_transaction(tx1)
    temp_store.insert_transaction(tx2)
    temp_store.insert_transaction(tx3)

    # Query 2025 alone.
    res_2025 = temp_store.query_transactions(year=2025)
    assert res_2025["count"] == 2
    assert res_2025["total_display"] == "£100.00"
    assert len(res_2025["merchant_breakdown"]) == 1
    assert res_2025["merchant_breakdown"][0]["merchant"] == "Amazon.co.uk"
    assert res_2025["merchant_breakdown"][0]["total_display"] == "£100.00"

    # Query merchant filter alone.
    res_apple = temp_store.query_transactions(merchant="Apple")
    assert res_apple["count"] == 1
    assert res_apple["total_display"] == "£100.00"


def test_format_aggregation_response(temp_store: TransactionStore) -> None:
    """Test markdown aggregation summary rendering."""
    tx = TransactionRecord(
        transaction_date="2025-08-20",
        year=2025,
        month=8,
        merchant="Wagamama",
        item_description="Partner Lunch",
        amount_minor=3550,
        currency="GBP",
        amount_display="£35.50",
        source_message_id="gmail#waga1#p1#c0",
        subject="Your receipt",
    )
    temp_store.insert_transaction(tx)

    res = temp_store.query_transactions(year=2025)
    md = temp_store.format_aggregation_response(
        "What did I buy last year?", res
    )

    assert "Total Identified Purchases" in md
    assert "£35.50" in md
    assert "Wagamama" in md
    assert "[gmail#waga1#p1#c0]" in md


def test_query_with_exclusions_and_thresholds(
    temp_store: TransactionStore,
) -> None:
    """Test SQL query with merchant exclusion and monetary thresholds."""
    tx1 = TransactionRecord(
        transaction_date="2025-02-10",
        year=2025,
        month=2,
        merchant="Amazon.co.uk",
        item_description="Cables",
        amount_minor=1500,
        currency="GBP",
        amount_display="£15.00",
        source_message_id="gmail#t1#p1#c0",
        subject="Amazon receipt",
    )
    tx2 = TransactionRecord(
        transaction_date="2025-03-12",
        year=2025,
        month=3,
        merchant="Apple",
        item_description="Mac Mini",
        amount_minor=89900,
        currency="GBP",
        amount_display="£899.00",
        source_message_id="gmail#t2#p1#c0",
        subject="Apple order",
    )
    tx3 = TransactionRecord(
        transaction_date="2025-04-15",
        year=2025,
        month=4,
        merchant="Dell UK",
        item_description="Monitor",
        amount_minor=32000,
        currency="GBP",
        amount_display="£320.00",
        source_message_id="gmail#t3#p1#c0",
        subject="Dell invoice",
    )

    temp_store.insert_transaction(tx1)
    temp_store.insert_transaction(tx2)
    temp_store.insert_transaction(tx3)

    # Exclude Amazon.
    res_no_amazon = temp_store.query_transactions(
        year=2025, exclude_merchant="Amazon"
    )
    assert res_no_amazon["count"] == 2
    merchants = [m["merchant"] for m in res_no_amazon["merchant_breakdown"]]
    assert "Amazon.co.uk" not in merchants
    assert "Apple" in merchants
    assert "Dell UK" in merchants

    # Filter with min_amount >= £200.00 (20000 pence).
    res_over_200 = temp_store.query_transactions(
        year=2025, min_amount=20000
    )
    assert res_over_200["count"] == 2
    assert res_over_200["total_display"] == "£1,219.00"


def test_compare_years_variance(temp_store: TransactionStore) -> None:
    """Test deterministic multi-year comparative variance computation."""
    tx_2024 = TransactionRecord(
        transaction_date="2024-05-10",
        year=2024,
        month=5,
        merchant="LexisNexis",
        item_description="Legal Research",
        amount_minor=50000,
        currency="GBP",
        amount_display="£500.00",
        source_message_id="gmail#ln24#p1#c0",
        subject="Annual Subscription",
    )
    tx_2025 = TransactionRecord(
        transaction_date="2025-05-10",
        year=2025,
        month=5,
        merchant="LexisNexis",
        item_description="Legal Research",
        amount_minor=60000,
        currency="GBP",
        amount_display="£600.00",
        source_message_id="gmail#ln25#p1#c0",
        subject="Annual Subscription",
    )

    temp_store.insert_transaction(tx_2024)
    temp_store.insert_transaction(tx_2025)

    comp = temp_store.compare_years(2024, 2025)
    assert comp["year_a"] == 2024
    assert comp["year_b"] == 2025
    assert comp["delta_display"] == "£+100.00"
    assert comp["pct_change"] == 20.0

    md = temp_store.format_comparison_response("Compare 2024 vs 2025", comp)
    assert "Comparative Financial Audit: 2024 vs 2025" in md
    assert "£+100.00 (+20.0%)" in md
