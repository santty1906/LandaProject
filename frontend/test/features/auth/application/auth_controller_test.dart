import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:landa_frontend/features/auth/application/auth_dependencies.dart';
import 'package:landa_frontend/features/auth/application/auth_providers.dart';
import 'package:landa_frontend/features/auth/application/auth_state.dart';
import 'package:landa_frontend/features/auth/domain/entities/auth_session.dart';
import 'package:landa_frontend/features/auth/domain/repositories/auth_repository.dart';

class FakeAuthRepository implements AuthRepository {
  FakeAuthRepository({this.initialSession});

  final AuthSession? initialSession;

  @override
  Future<AuthSession?> restoreSession() async => initialSession;

  @override
  Future<AuthSession> signInPlaceholder() async => const AuthSession(accessToken: 'token');

  @override
  Future<void> signOut() async {}
}

void main() {
  test('auth controller transitions to unauthenticated when no stored session', () async {
    final container = ProviderContainer(
      overrides: [
        authRepositoryProvider.overrideWithValue(FakeAuthRepository()),
      ],
    );
    addTearDown(container.dispose);

    expect(container.read(authControllerProvider).status, AuthStatus.loading);

    await Future<void>.delayed(Duration.zero);

    expect(
      container.read(authControllerProvider).status,
      AuthStatus.unauthenticated,
    );
  });
}
