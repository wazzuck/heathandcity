"""
Continuous Sovereign Indexer Runner for Heath & City Practice Vault.

Purpose:
  Coordinates persistent, non-blocking ingestion sweeps across user Gmail
  archives and Google Drive documents. Runs iterative batches against the
  local appliance Application Programming Interface (API) daemon, tracking
  milestones and preventing quota exhaustion.

Deliberately Not For:
  Direct database mutation or cloud egress outside the authenticated local
  daemon at 127.0.0.1:8080.

Invariants:
  1. All indexed data is written to external appliance storage. Zero customer
     data or personal correspondence is stored in the Git repository.
  2. Runs continuously until interrupted or until all correspondence is
     exhausted.
"""

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, Optional


API_BASE = "http://127.0.0.1:8080/api"
DEFAULT_BATCH_SIZE = 250
MAX_CONSECUTIVE_ERRORS = 10


def trigger_gmail_batch(
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> Optional[Dict[str, Any]]:
    """
    Trigger one checkpointed batch sweep for Gmail correspondence.

    Execution steps:
      1. Step 1: Construct POST request to local sync-gmail endpoint.
      2. Step 2: Transmit HTTP request and parse JSON payload.
      3. Step 3: Handle transient network or rate-limiting exceptions.

    Args:
      batch_size: Maximum messages to fetch in single batch.

    Returns:
      Dictionary containing sync results or None on failure.
    """
    url = f"{API_BASE}/google/sync-gmail?max_messages={batch_size}&use_checkpoint=true"
    req = urllib.request.Request(url, data=b"", method="POST")

    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            if response.status == 200:
                body = response.read().decode("utf-8")
                return json.loads(body)
    except urllib.error.HTTPError as exc:
        print(f"[Error] HTTP {exc.code}: {exc.reason}", flush=True)
    except urllib.error.URLError as exc:
        print(f"[Error] Connection error: {exc.reason}", flush=True)
    except Exception as exc:
        print(f"[Error] Unexpected failure: {exc}", flush=True)

    return None


def fetch_vault_statistics() -> Optional[Dict[str, Any]]:
    """
    Fetch live indexing statistics from the appliance daemon.

    Returns:
      Dictionary containing tracked documents, chunks, and source counts.
    """
    url = f"{API_BASE}/stats"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            if response.status == 200:
                body = response.read().decode("utf-8")
                return json.loads(body)
    except Exception:
        pass
    return None


def run_continuous_loop(
    duration_seconds: int = 86400,  # 24 hours
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """
    Run continuous indexing loop for up to specified duration.

    Execution steps:
      1. Step 1: Record loop start timestamp and initialize counters.
      2. Step 2: Trigger Gmail batch sweep with persistent checkpointing.
      3. Step 3: Log batch results and print cumulative statistics.
      4. Step 4: Gracefully back off if rate-limited or end of archive reached.
      5. Step 5: Terminate cleanly when duration expires.

    Args:
      duration_seconds: Maximum operational duration in seconds.
      batch_size: Message count per ingestion batch.
    """
    start_time = time.time()
    batch_index = 0
    consecutive_errors = 0

    print(
        f"Starting continuous indexing loop at "
        f"{datetime.now(timezone.utc).isoformat()} "
        f"for maximum {duration_seconds} seconds...",
        flush=True,
    )

    while (time.time() - start_time) < duration_seconds:
        batch_index += 1
        print(
            f"\n--- [Batch #{batch_index}] Initiating sweep "
            f"({batch_size} messages) ---",
            flush=True,
        )

        result = trigger_gmail_batch(batch_size=batch_size)

        if result and result.get("status") == "success":
            consecutive_errors = 0
            fetched = result.get("messages_fetched", 0)
            indexed = result.get("chunks_indexed", 0)
            volume = result.get("total_vault_volume", 0)

            print(
                f"[Batch #{batch_index} Success] Messages fetched: {fetched}, "
                f"Chunks indexed: {indexed}, Total vault chunks: {volume}",
                flush=True,
            )

            stats = fetch_vault_statistics()
            if stats:
                tracked = stats.get("total_documents_tracked", 0)
                words = stats.get("total_words_indexed", 0)
                mb = stats.get("total_megabytes_indexed", 0.0)
                breakdown = stats.get("source_breakdown", {})
                print(
                    f"[Telemetry] Tracked docs: {tracked} | Words: {words:,} "
                    f"| Storage: {mb} MB | Sources: {breakdown}",
                    flush=True,
                )

            # If zero messages returned, we have reached the end of the archive stream.
            if fetched == 0:
                print(
                    "[Notice] Current archive sweep reached end of stream. "
                    "Pausing 30 seconds before next check...",
                    flush=True,
                )
                time.sleep(30)
            else:
                # Controlled pause between batches to honour Google API quotas
                # (1,250 quota units per 250 messages; limit is 6,000 units/min).
                time.sleep(12)
        else:
            consecutive_errors += 1
            print(
                f"[Warning] Batch #{batch_index} failed. "
                f"Consecutive errors: {consecutive_errors}",
                flush=True,
            )
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print(
                    "[Alert] Maximum error threshold reached. Backing off 60s.",
                    flush=True,
                )
                time.sleep(60)
            else:
                time.sleep(10)

    elapsed = round(time.time() - start_time, 1)
    print(
        f"\nContinuous indexing window finished after {elapsed} seconds.",
        flush=True,
    )


if __name__ == "__main__":
    run_continuous_loop()
