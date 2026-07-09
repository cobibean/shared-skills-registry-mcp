# Brand Character Pass Memory - 2026-05-18

## Session summary

- Added more visual character to the homepage while preserving the calm,
  professional tone.
- Chose one approved illustration direction and replaced a generic centered
  hero with a more editorial layout.

## What we learned

- The page can carry more personality without becoming noisy when the
  illustration supports the existing brand tone.
- Mobile needs a separately considered crop instead of simply squeezing the
  desktop composition down.

## Decisions made

- Desktop hero should be left-aligned with a right-side illustration.
- Mobile should hide the illustration for now until a mobile-specific crop is
  approved.
- The rose accent is approved as the emotional accent color.
- Temporary design-review routes are useful locally but should not ship as
  production routes.

## Open decisions

- Should the header tagline remain after client review?

## Files created or changed

- `src/app/page.tsx`
- `src/components/hero-illustration.tsx`
- `src/components/squiggle-divider.tsx`
- `src/app/globals.css`
- `.gitignore`

## Source-of-truth docs

- `docs/prd.md`
- `docs/brand-guide.md`
- `docs/plans/2026-05-18-brand-character-plan.md`

## Commands and verification

```bash
npm run lint
npm run build
```

Visual verification:

- Checked desktop homepage at `1440x1000`.
- Checked mobile homepage at `390x844`.

## Gotchas and constraints

- Do not expose placeholder language in public UI.
- Client-sensitive placeholder status belongs in docs or memory only.

## Open questions

- Should the header tagline remain after client review?

## Recommended next work

- Run one final dark-mode pass before launch.
