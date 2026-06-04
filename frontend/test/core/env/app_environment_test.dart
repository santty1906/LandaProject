import 'package:flutter_test/flutter_test.dart';
import 'package:landa_frontend/core/env/app_environment.dart';
import 'package:landa_frontend/core/errors/config_exception.dart';

void main() {
  test('fromMap builds environment when required keys exist', () {
    final environment = AppEnvironment.fromMap({
      'API_BASE_URL': 'http://localhost:8000/api/v1',
      'APP_ENV': 'development',
    });

    expect(environment.apiBaseUrl, 'http://localhost:8000/api/v1');
    expect(environment.appEnv, 'development');
  });

  test('fromMap throws when API_BASE_URL is missing', () {
    expect(
      () => AppEnvironment.fromMap({'APP_ENV': 'development'}),
      throwsA(isA<ConfigException>()),
    );
  });
}
