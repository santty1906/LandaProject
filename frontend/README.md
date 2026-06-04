# Frontend (Flutter)

Flutter app scaffold for the mobile banking client.

## Foundation modules

- `lib/app`: app bootstrap, routing, dependency setup
- `lib/core`: shared utilities (env, networking, theme, storage, security contracts)
- `lib/features`: feature-first modules (`auth`, `dashboard`, `session`)
- `test` and `integration_test`: testing structure

## Flavors

- `lib/main_development.dart`
- `lib/main_staging.dart`
- `lib/main_production.dart`

Each flavor loads its environment file through centralized bootstrap.
