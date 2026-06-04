import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'auth_dependencies.dart';
import 'auth_state.dart';

class AuthController extends Notifier<AuthState> {
  @override
  AuthState build() {
    _restoreSession();
    return const AuthState(status: AuthStatus.loading);
  }

  Future<void> _restoreSession() async {
    final repository = ref.read(authRepositoryProvider);
    final session = await repository.restoreSession();

    if (session == null) {
      state = const AuthState(status: AuthStatus.unauthenticated);
      return;
    }

    state = AuthState(
      status: AuthStatus.authenticated,
      token: session.accessToken,
    );
  }

  Future<void> signInPlaceholder() async {
    final repository = ref.read(authRepositoryProvider);
    final session = await repository.signInPlaceholder();

    state = AuthState(
      status: AuthStatus.authenticated,
      token: session.accessToken,
    );
  }

  Future<void> signOut() async {
    await ref.read(authRepositoryProvider).signOut();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }
}
