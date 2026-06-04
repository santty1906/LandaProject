enum AppFlavor {
  development,
  staging,
  production;

  String get envFileName {
    switch (this) {
      case AppFlavor.development:
        return '.env.development';
      case AppFlavor.staging:
        return '.env.staging';
      case AppFlavor.production:
        return '.env.production';
    }
  }
}
