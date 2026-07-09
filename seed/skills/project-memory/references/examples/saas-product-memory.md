# Billing Entitlements Memory - 2026-05-18

## Session summary

- Reviewed the v0 billing and entitlement flow before implementation.
- Confirmed the product should collect a setup fee before provisioning and only
  keep hosting active after successful deployment.
- No app code was scaffolded in this session.

## What we learned

- Billing and deployment state need to be modeled together because deployment
  failure can affect whether ongoing hosting should stay active.
- Admin review is the safer v0 path for unusual refund or provisioning cases.

## Decisions made

- Failed deployments should not leave a monthly subscription active.
- Admin review is preferred over automatic refund logic for edge cases in v0.
- Billing state should be treated as a server-side authorization concern, not
  only a UI state.

## Open decisions

- Should admin review be represented as a deployment state, billing state, or
  both?

## Files created or changed

- `docs/plans/2026-05-18-billing-entitlements-review.md`

## Source-of-truth docs

- `docs/planning/billing-entitlements.md`
- `docs/planning/deployment-state-machine.md`
- `docs/planning/security-secrets.md`

## Commands and verification

```bash
rg -n "subscription|entitlement|refund|admin_review" docs
```

## Gotchas and constraints

- Do not store provider keys or payment secrets in memory.
- Treat route handlers and server actions as the authorization boundary.

## Open questions

- Should admin review be represented as a deployment state, billing state, or
  both?

## Recommended next work

- Align database schema with the billing state machine before implementing
  Stripe webhooks.
