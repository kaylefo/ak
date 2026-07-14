# Tsubo Web

Next.js 15 frontend for the Tsubo vacant property registry.

## Development

```bash
pnpm install
pnpm --filter @tsubo/contracts build
pnpm --filter @tsubo/ui build
pnpm --filter @tsubo/web dev
```

## Environment

Copy `.env.example` to `.env.local` and set `NEXT_PUBLIC_API_URL`.

## Tests

```bash
pnpm --filter @tsubo/web test        # vitest unit tests
pnpm --filter @tsubo/web test:e2e    # playwright e2e
```
