"""Quickstart — mirrors https://docs.presscart.com/getting-started/quickstart.

Run with:
    PRESSCART_API_TOKEN=pc_... uv run python examples/quickstart.py
"""

from __future__ import annotations

import os
import sys

from pypresscart import (
    CheckoutLineItem,
    CheckoutRequest,
    PresscartAPIError,
    PresscartClient,
)


def main() -> int:
    token = os.environ.get("PRESSCART_API_TOKEN")
    if not token:
        print("set PRESSCART_API_TOKEN", file=sys.stderr)
        return 1

    with PresscartClient(api_token=token) as client:
        # 1. Verify token
        me = client.auth.whoami()
        print(f"team={me.team_id} type={me.token_type} scopes={me.scopes}")

        # 2. Browse outlets
        outlets = client.outlets.list(limit=3)
        for row in outlets.records:
            print(f"- {row.outlet_name} (product_id={row.id})")

        # 3. Place an order (demonstration — uncomment + fill in IDs)
        _demo_checkout = CheckoutRequest(
            profile_id="YOUR_PROFILE_ID",
            line_items=[CheckoutLineItem(product_id="YOUR_PRODUCT_ID", quantity=1)],
            discount=0,
        )
        # order = client.orders.create_checkout(_demo_checkout)
        # print(order.reference_number, order.checkout_link)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PresscartAPIError as exc:
        print(f"API error [{exc.status_code}] {exc.name}: {exc.message}", file=sys.stderr)
        sys.exit(2)
