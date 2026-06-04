import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/application/auth_providers.dart';
import '../env/env_providers.dart';
import 'api_error.dart';

final dioProvider = Provider<Dio>((ref) {
  final env = ref.watch(appEnvironmentProvider);
  final authState = ref.watch(authControllerProvider);

  final dio = Dio(
    BaseOptions(
      baseUrl: env.apiBaseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
    ),
  );

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) {
        final token = authState.token;
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        final mappedError = ApiError(
          error.message ?? 'Unexpected network error',
          statusCode: error.response?.statusCode,
        );
        handler.reject(
          DioException(
            requestOptions: error.requestOptions,
            error: mappedError,
            response: error.response,
            type: error.type,
          ),
        );
      },
    ),
  );

  return dio;
});
