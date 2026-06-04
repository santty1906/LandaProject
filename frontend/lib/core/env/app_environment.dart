import 'package:flutter_dotenv/flutter_dotenv.dart';

import '../errors/config_exception.dart';

class AppEnvironment {
  const AppEnvironment({required this.apiBaseUrl, required this.appEnv});

  final String apiBaseUrl;
  final String appEnv;

  static AppEnvironment fromMap(Map<String, String> values) {
    final apiBaseUrl = values['API_BASE_URL']?.trim();
    final appEnv = values['APP_ENV']?.trim();

    if (apiBaseUrl == null || apiBaseUrl.isEmpty) {
      throw ConfigException('Missing required env: API_BASE_URL');
    }

    if (appEnv == null || appEnv.isEmpty) {
      throw ConfigException('Missing required env: APP_ENV');
    }

    return AppEnvironment(apiBaseUrl: apiBaseUrl, appEnv: appEnv);
  }

  static Future<AppEnvironment> loadFromFile(String fileName) async {
    await dotenv.load(fileName: fileName);
    return fromMap(dotenv.env);
  }
}
