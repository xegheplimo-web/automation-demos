# Fiverr inbox — spam pattern audit

Date: 2026-11-20. Seller `@btc207` (Vietnam).

## Summary

Every inbound conversation so far is the same **scammer template** dressed up as a buyer.
None of them has an order. `manage_orders` shows **0** in every bucket.

Pattern: the account opens the chat, claims work is already finished, and attaches a
small `.html` file (or an external URL) as "the deliverable". The point is to get the
seller to open the file or visit the link.

## Verified facts per conversation

| Conversation | Order? | Account created | From | Attachment | Content |
|---|---|---|---|---|---|
| `sharkphoenix188` | none | Nov 2026 | United Kingdom | `1.html` (269 byte) | "I've finished all tasks on my side — the entire requested workload is complete." + "I'm sending the complete details below. Please check all of it thoroughly." |
| `zoe_27469` | none | Nov 2026 | Colombia | URL | "I've chosen the service, filled in the information, and sent my order." + "Reference : https://mentor-core.com" |
| `greg32679m` | none | Nov 2026 | United Kingdom | — | conversation shows "greg32679m is no longer available. Messaging unavailable" |
| `Heather B.` | none | — | — | — | "My order is ready. 🤝 Please open my project, review the details, and confirm the order:" |
| `k_nate_4994` | none | — | — | — | same template |
| `b_scott_e1704` | none | — | — | — | same template |
| `Blanka R.` | none | — | — | — | same template |
| `d_fuller_7317` | none | — | — | — | profile reads "d_fuller_7317 is no longer available" |

Fiverr's own UI on `sharkphoenix188` states: **"This client has no orders with you."**

## What was done

- `sharkphoenix188` — **replied** on Sếp's instruction (2026-11-20 01:07).
  Message asks for the plain-text brief (gig + package, URLs, fields, output format,
  deadline), states that attached files and links are not opened, and asks the client to
  keep payment on Fiverr. Verified sent: composer cleared, Send re-disabled, message
  shows in thread with the "Me" badge.
- `k_nate_4994`, `b_scott_e1704`, `Blanka R.`, `d_fuller_7317` — moved to spambox
  (2026-11-19).
- `zoe_27469` — "Move to spambox" clicked; persistence not yet confirmed after reload.
- `greg32679m` — messaging unavailable, nothing to do.

## Rules applied

- Never open an `.html` attachment or visit an external link from an unsolicited
  Fiverr chat. The 269-byte file is exactly the size of a redirect/phishing stub.
- Never treat "I've placed my order" as an order. Verify against `manage_orders`.
- Never move payment off-platform, and never share personal information.
- Reply only with text that asks for the brief in plain text, so a scammer gets nothing
  to click.

## Outstanding

- Confirm `zoe_27469` actually moved to spambox (read `/conversations/type/spam`
  after the PerimeterX cooldown).
- `Heather B.`, `k_nate_4994`, `b_scott_e1704`, `Blanka R.`, `d_fuller_7317` spambox
  persistence was never read back either — same check applies.
