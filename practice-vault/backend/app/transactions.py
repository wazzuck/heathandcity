"""
Structured Transaction Extraction and Deterministic Aggregation Engine.

Purpose:
  Provides deterministic aggregation and accounting recovery for financial
  records (receipts, fee notes, invoices, and purchase confirmations) indexed
  in the Practice Vault. Implements Path B from the architectural
  recommendations: offloading arithmetic and multi-document purchase queries
  from Small Language Models (SLMs) to Structured Query Language (SQL).

Deliberately Not For:
  Executing live bank transfers, initiating accounting debits, or modifying
  source client correspondence.

Invariants:
  1. All currency calculations are executed in integer minor units (e.g. pence
     or cents) to prevent floating-point rounding errors.
  2. Language models are never asked to perform arithmetic; totals and sums
     are computed strictly by deterministic SQLite aggregation.
  3. All monetary summaries provide verifiable source email or document
     identifiers.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import email.utils
from pathlib import Path
import re
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from .config import settings


@dataclass
class TransactionRecord:
    """
    Structured ledger row representing a verified purchase or disbursement.

    Attributes:
      transaction_date: Date string formatted as YYYY-MM-DD.
      year: Gregorian calendar year as integer (e.g. 2025).
      month: Calendar month integer (1 to 12).
      merchant: Counterparty, retailer, vendor, or issuing organisation.
      item_description: Extracted item, service, or subject synopsis.
      amount_minor: Monetary amount in integer minor units (e.g. 6474 pence).
      currency: Three-letter International Organisation for Standardisation
        (ISO) currency code (default 'GBP').
      amount_display: Human-readable formatted string (e.g. '£64.74').
      source_message_id: Originating Gmail message or document identifier.
      subject: Full correspondence subject line.
      confidence: Statistical confidence score between 0.0 and 1.0.
    """

    transaction_date: str
    year: int
    month: int
    merchant: str
    item_description: str
    amount_minor: int
    currency: str
    amount_display: str
    source_message_id: str
    subject: str
    confidence: float = 1.0


class TransactionStore:
    """
    Manages deterministic transaction extraction, indexing, and querying.

    Attributes:
      db_path: Filesystem path to SQLite transaction database.
    """

    # Regex patterns for detecting currency and monetary amounts.
    AMOUNT_PATTERN = re.compile(
        r"(?:total(?: paid)?|grand total|order total|charged|amount paid|"
        r"subtotal|balance due)?[:\s]*([£$€])\s*([0-9]{1,4}(?:,[0-9]{3})*"
        r"\.[0-9]{2})",
        re.IGNORECASE,
    )

    # Keywords indicating purchase, receipt, order, or billing statement.
    PURCHASE_INDICATORS = [
        "order",
        "receipt",
        "invoice",
        "payment",
        "purchased",
        "booking confirmation",
        "ticket",
        "tax invoice",
        "disbursement",
        "fee note",
    ]

    # Exclusions for shipping updates to prevent double-counting orders.
    SHIPPING_EXCLUSIONS = [
        "out for delivery",
        "delivered:",
        "dispatched:",
        "shipment tracking",
    ]

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialise transaction database connection and schema.

        Args:
          db_path: Path to transactions.db file (defaults to data_dir).
        """
        if db_path is not None:
            self.db_path = Path(db_path).resolve()
        else:
            self.db_path = settings.data_dir / "transactions.db"

        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a thread-safe connection with dictionary row access."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self) -> None:
        """
        Create structured transactions table and supporting indices.

        Execution steps:
          1. Step 1: Ensure parent directory exists.
          2. Step 2: Create transactions table with unique deduplication key.
          3. Step 3: Create indices covering year, date, and merchant.
        """
        # Step 1: Ensure directory exists.
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            # Step 2: Create transactions table.
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_date TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    merchant TEXT NOT NULL,
                    item_description TEXT NOT NULL,
                    amount_minor INTEGER NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'GBP',
                    amount_display TEXT NOT NULL,
                    source_message_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    created_at TEXT NOT NULL,
                    UNIQUE(source_message_id, amount_minor, merchant)
                );
                """
            )
            # Step 3: Create indices.
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tx_year "
                "ON transactions(year);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tx_date "
                "ON transactions(transaction_date);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tx_merchant "
                "ON transactions(merchant);"
            )
            conn.commit()

    @staticmethod
    def _clean_merchant(sender: str) -> str:
        """Extract clean merchant or counterparty name from sender header."""
        sender_clean = sender.strip()
        if "<" in sender_clean:
            display_part = sender_clean.split("<")[0].strip().strip("\"'")
            if display_part:
                return display_part
            email_part = sender_clean.split("<")[1].split(">")[0].strip()
            domain = email_part.split("@")[-1].lower()
            return domain
        return sender_clean.strip("\"'")

    @staticmethod
    def _parse_email_date(date_header: str) -> Tuple[str, int, int]:
        """
        Parse RFC 2822 email date header into (YYYY-MM-DD, year, month).

        Returns:
          Tuple containing date string, four-digit year, and two-digit month.
        """
        try:
            parsed = email.utils.parsedate_to_datetime(date_header)
            return (
                parsed.strftime("%Y-%m-%d"),
                parsed.year,
                parsed.month,
            )
        except Exception:
            # Fallback to current UTC date if header is missing or unparseable.
            now = datetime.now(timezone.utc)
            return now.strftime("%Y-%m-%d"), now.year, now.month

    def extract_from_email(
        self,
        chunk_id: str,
        subject: str,
        sender: str,
        date_header: str,
        text: str,
    ) -> Optional[TransactionRecord]:
        """
        Extract structured transaction data from email text.

        Execution steps:
          1. Step 1: Validate whether subject or text indicates a purchase.
          2. Step 2: Skip shipping delivery notices to avoid duplicate orders.
          3. Step 3: Extract merchant name from sender header.
          4. Step 4: Parse transaction date, year, and month.
          5. Step 5: Locate explicit total or monetary amounts in text.
          6. Step 6: Construct and return TransactionRecord.

        Args:
          chunk_id: Document chunk identifier (e.g. 'gmail#abc123#p1#c0').
          subject: Email subject line.
          sender: Email sender address or name.
          date_header: Raw Date header string.
          text: Full email body text.

        Returns:
          TransactionRecord if a purchase is identified, otherwise None.
        """
        # Step 1: Check purchase indicators.
        combined_meta = f"{subject} {text[:500]}".lower()
        if not any(k in combined_meta for k in self.PURCHASE_INDICATORS):
            return None

        # Step 2: Avoid delivery notices if order confirmation is expected.
        subject_lower = subject.lower()
        if any(ex in subject_lower for ex in self.SHIPPING_EXCLUSIONS):
            return None

        # Step 3: Clean merchant name.
        merchant = self._clean_merchant(sender)
        if not merchant:
            merchant = "Unknown Counterparty"

        # Step 4: Parse transaction date.
        tx_date, tx_year, tx_month = self._parse_email_date(date_header)

        # Step 5: Locate currency and amounts.
        matches = self.AMOUNT_PATTERN.findall(text)
        if not matches:
            return None

        # Prioritise the final amount in a receipt, which typically represents
        # the grand total or amount charged.
        symbol, amount_str = matches[-1]
        amount_clean = amount_str.replace(",", "")
        try:
            amount_float = float(amount_clean)
            amount_minor = int(round(amount_float * 100))
        except ValueError:
            return None

        # Filter out trivial amounts (< £0.50) or implausible sums (> £500,000)
        # to safeguard against tracking numbers parsed as currency.
        if amount_minor < 50 or amount_minor > 50_000_000:
            return None

        currency_map = {"£": "GBP", "$": "USD", "€": "EUR"}
        currency = currency_map.get(symbol, "GBP")
        amount_display = f"{symbol}{amount_float:,.2f}"

        item_desc = subject
        if item_desc.lower().startswith("subject:"):
            item_desc = item_desc[8:].strip()

        # Step 6: Return populated TransactionRecord.
        return TransactionRecord(
            transaction_date=tx_date,
            year=tx_year,
            month=tx_month,
            merchant=merchant,
            item_description=item_desc,
            amount_minor=amount_minor,
            currency=currency,
            amount_display=amount_display,
            source_message_id=chunk_id,
            subject=subject,
            confidence=0.95,
        )

    def insert_transaction(self, tx: TransactionRecord) -> bool:
        """
        Insert transaction record into database, ignoring duplicates.

        Returns:
          True if inserted, False if record already existed.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO transactions (
                    transaction_date, year, month, merchant,
                    item_description, amount_minor, currency,
                    amount_display, source_message_id, subject,
                    confidence, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    tx.transaction_date,
                    tx.year,
                    tx.month,
                    tx.merchant,
                    tx.item_description,
                    tx.amount_minor,
                    tx.currency,
                    tx.amount_display,
                    tx.source_message_id,
                    tx.subject,
                    tx.confidence,
                    now_str,
                ),
            )
            conn.commit()
            return cur.rowcount > 0

    def scan_fts_database(
        self,
        fts_db_path: Optional[Path] = None,
        limit: int = 10000,
    ) -> int:
        """
        Batch-scan candidate emails from SQLite FTS index into the
        transaction store.

        Execution steps:
          1. Step 1: Open read-only connection to FTS database.
          2. Step 2: Query candidate emails matching financial keywords.
          3. Step 3: Extract transaction records from message text.
          4. Step 4: Persist records into transactions table.
        """
        target_fts = fts_db_path or (
            settings.data_dir / "practice_fts.db"
        )
        if not target_fts.exists():
            return 0

        fts_conn = sqlite3.connect(f"file:{target_fts}?mode=ro", uri=True)
        fts_conn.row_factory = sqlite3.Row
        cur = fts_conn.cursor()

        # Step 2: Select candidate emails.
        query = """
            SELECT chunk_id, file_name, text FROM practice_fts
            WHERE practice_fts MATCH
                'order OR receipt OR invoice OR payment OR total'
              AND chunk_id LIKE 'gmail%'
            LIMIT ?;
        """
        cur.execute(query, (limit,))
        rows = cur.fetchall()

        inserted_count = 0
        for r in rows:
            chunk_id = r["chunk_id"]
            text = r["text"]
            file_name = r["file_name"]

            # Extract headers from stored text.
            subj_m = re.search(r"Subject:\s*(.+)", text)
            subj = subj_m.group(1).strip() if subj_m else file_name
            from_m = re.search(r"From:\s*(.+)", text)
            sender = from_m.group(1).strip() if from_m else ""
            date_m = re.search(r"Date:\s*(.+)", text)
            date_h = date_m.group(1).strip() if date_m else ""

            tx = self.extract_from_email(
                chunk_id=chunk_id,
                subject=subj,
                sender=sender,
                date_header=date_h,
                text=text,
            )
            if tx and self.insert_transaction(tx):
                inserted_count += 1

        fts_conn.close()
        return inserted_count

    def query_transactions(
        self,
        year: Optional[int] = None,
        merchant: Optional[str] = None,
        exclude_merchant: Optional[str] = None,
        min_amount: Optional[int] = None,
        max_amount: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Query transactions with deterministic SQL sums, counts, and grouping.

        Args:
          year: Optional calendar year filter.
          merchant: Optional counterparty substring filter.
          exclude_merchant: Optional counterparty substring to exclude.
          min_amount: Optional minimum amount in minor currency units (pence).
          max_amount: Optional maximum amount in minor currency units (pence).
          date_from: Optional inclusive start date (YYYY-MM-DD).
          date_to: Optional inclusive end date (YYYY-MM-DD).
          limit: Maximum rows returned.

        Returns:
          Dictionary of totals, merchant groupings, and transaction rows.
        """
        conditions = []
        params: List[Any] = []

        if year is not None:
            conditions.append("year = ?")
            params.append(year)
        if merchant is not None:
            conditions.append("merchant LIKE ?")
            params.append(f"%{merchant}%")
        if exclude_merchant is not None:
            conditions.append("merchant NOT LIKE ?")
            params.append(f"%{exclude_merchant}%")
        if min_amount is not None:
            conditions.append("amount_minor >= ?")
            params.append(min_amount)
        if max_amount is not None:
            conditions.append("amount_minor <= ?")
            params.append(max_amount)
        if date_from is not None:
            conditions.append("transaction_date >= ?")
            params.append(date_from)
        if date_to is not None:
            conditions.append("transaction_date <= ?")
            params.append(date_to)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        with self._get_connection() as conn:
            # 1. Total count and sum.
            tot_row = conn.execute(
                f"""
                SELECT count(*) as tx_count,
                       COALESCE(SUM(amount_minor), 0) as total_minor
                FROM transactions
                {where_clause};
                """,
                params,
            ).fetchone()

            tx_count = tot_row["tx_count"]
            total_minor = tot_row["total_minor"]
            total_float = total_minor / 100.0

            # 2. Top merchants by expenditure.
            merch_rows = conn.execute(
                f"""
                SELECT merchant,
                       count(*) as count,
                       COALESCE(SUM(amount_minor), 0) as merch_minor
                FROM transactions
                {where_clause}
                GROUP BY merchant
                ORDER BY merch_minor DESC
                LIMIT 10;
                """,
                params,
            ).fetchall()

            merchant_summary = [
                {
                    "merchant": r["merchant"],
                    "count": r["count"],
                    "total_minor": r["merch_minor"],
                    "total_display": f"£{r['merch_minor'] / 100.0:,.2f}",
                }
                for r in merch_rows
            ]

            # 3. Detailed individual transactions.
            tx_rows = conn.execute(
                f"""
                SELECT id, transaction_date, year, month, merchant,
                       item_description, amount_minor, currency,
                       amount_display, source_message_id, subject
                FROM transactions
                {where_clause}
                ORDER BY transaction_date DESC
                LIMIT ?;
                """,
                params + [limit],
            ).fetchall()

            transactions = [dict(r) for r in tx_rows]

        return {
            "count": tx_count,
            "total_minor": total_minor,
            "total_display": f"£{total_float:,.2f}",
            "merchant_breakdown": merchant_summary,
            "transactions": transactions,
        }

    def format_aggregation_response(
        self,
        user_query: str,
        query_result: Dict[str, Any],
    ) -> str:
        """
        Format deterministic aggregation findings into an institutional summary.

        Execution steps:
          1. Step 1: Render headline totals and record volume.
          2. Step 2: Render merchant breakdown table.
          3. Step 3: Render itemised transaction log with citations.
        """
        count = query_result.get("count", 0)
        total_str = query_result.get("total_display", "£0.00")
        merchants = query_result.get("merchant_breakdown", [])
        txs = query_result.get("transactions", [])

        if count == 0:
            return (
                "The practice financial ledger contains no recorded "
                "transactions matching the specified criteria."
            )

        lines: List[str] = [
            f"### Financial Reconciliation & Purchase Summary",
            f"",
            f"- **Total Identified Purchases**: {count} transactions",
            f"- **Cumulative Expenditure**: {total_str}",
            f"",
        ]

        if merchants:
            lines.append("#### Principal Counterparties & Merchants")
            lines.append("| Counterparty | Transactions | Cumulative Spend |")
            lines.append("| :--- | :--- | :--- |")
            for m in merchants:
                lines.append(
                    f"| {m['merchant']} | {m['count']} | {m['total_display']} |"
                )
            lines.append("")

        if txs:
            lines.append("#### Itemised Transaction Ledger")
            lines.append(
                "| Date | Merchant | Item / Description | Amount | Citation |"
            )
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for t in txs[:25]:
                clean_desc = t['item_description'][:40].replace("|", "/")
                lines.append(
                    f"| {t['transaction_date']} | {t['merchant']} | "
                    f"{clean_desc} | {t['amount_display']} | "
                    f"[{t['source_message_id']}] |"
                )
            if len(txs) > 25:
                lines.append(
                    f"\n*(Showing 25 of {len(txs)} retrieved records)*"
                )

        return "\n".join(lines)

    def compare_years(
        self,
        year_a: int,
        year_b: int,
        merchant: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compare financial performance and expenditure across two calendar
        years.

        Execution steps:
          1. Step 1: Query deterministic totals and record counts for year_a.
          2. Step 2: Query deterministic totals and record counts for year_b.
          3. Step 3: Compute exact numerical difference and percentage variance.

        Args:
          year_a: Baseline calendar year (e.g. 2024).
          year_b: Comparison calendar year (e.g. 2025).
          merchant: Optional counterparty filter applied to both periods.

        Returns:
          Dictionary containing comparative summaries and variance figures.
        """
        res_a = self.query_transactions(
            year=year_a, merchant=merchant, limit=10
        )
        res_b = self.query_transactions(
            year=year_b, merchant=merchant, limit=10
        )

        tot_a = res_a.get("total_minor", 0)
        tot_b = res_b.get("total_minor", 0)
        diff_minor = tot_b - tot_a
        diff_float = diff_minor / 100.0

        pct_change = 0.0
        if tot_a > 0:
            pct_change = (diff_minor / tot_a) * 100.0

        return {
            "year_a": year_a,
            "year_b": year_b,
            "merchant_filter": merchant,
            "summary_a": res_a,
            "summary_b": res_b,
            "delta_minor": diff_minor,
            "delta_display": f"£{diff_float:+,.2f}",
            "pct_change": round(pct_change, 1),
        }

    def format_comparison_response(
        self,
        user_query: str,
        comp_result: Dict[str, Any],
    ) -> str:
        """
        Format comparative financial findings into an executive briefing table.

        Args:
          user_query: User inquiry string in plain English.
          comp_result: Output from compare_years method.

        Returns:
          Structured markdown analysis highlighting variance and changes.
        """
        y_a = comp_result["year_a"]
        y_b = comp_result["year_b"]
        sum_a = comp_result["summary_a"]
        sum_b = comp_result["summary_b"]
        delta_str = comp_result["delta_display"]
        pct_val = comp_result["pct_change"]
        pct_sign = "+" if pct_val > 0 else ""

        lines = [
            f"### Comparative Financial Audit: {y_a} vs {y_b}",
            "",
            f"| Period / Metric | {y_a} | {y_b} | Variance |",
            f"| :--- | :--- | :--- | :--- |",
            f"| **Cumulative Spend** | {sum_a.get('total_display', '£0.00')} | "
            f"{sum_b.get('total_display', '£0.00')} | "
            f"**{delta_str} ({pct_sign}{pct_val}%)** |",
            f"| **Transaction Volume** | {sum_a.get('count', 0)} orders | "
            f"{sum_b.get('count', 0)} orders | "
            f"{sum_b.get('count', 0) - sum_a.get('count', 0):+d} orders |",
            "",
            f"#### Top Counterparties in {y_b}",
            "| Counterparty | Transactions | Cumulative Spend |",
            "| :--- | :--- | :--- |",
        ]

        for m in sum_b.get("merchant_breakdown", [])[:5]:
            lines.append(
                f"| {m['merchant']} | {m['count']} | {m['total_display']} |"
            )

        return "\n".join(lines)
