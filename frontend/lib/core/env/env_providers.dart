import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app_environment.dart';

final appEnvironmentProvider = Provider<AppEnvironment>(
  (ref) => throw UnimplementedError('AppEnvironment must be overridden at bootstrap.'),
);
