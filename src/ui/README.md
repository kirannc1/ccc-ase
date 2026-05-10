# CCC ASE UI (PoC)

## Setup
- From `D:\\kiran\\poc\\poc\\src\\ui` run: `npm i`
- Dev: `npm run start`
- Tests: `npm run test` / `npm run test:coverage`

## Architecture
- `components/`: reusable UI building blocks
- `features/`: screens (container + hooks + service + types)
- `services/`: typed API client + runtime adapters
- `types/`: shared domain types + zod validators
- `test/`: MSW + test utilities

## Testing
- Jest + React Testing Library
- MSW for deterministic API responses
- Service layer tests validate error handling + parsing

