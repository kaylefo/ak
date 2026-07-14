#!/usr/bin/env python3
"""Direct OpenSearch reindex without Temporal."""

from __future__ import annotations

import asyncio
import sys

from tsubo_api.search.indexing import reindex_all


async def main() -> None:
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    result = await reindex_all(batch_size=batch_size)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
