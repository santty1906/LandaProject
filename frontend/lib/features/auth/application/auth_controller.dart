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
    try {
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
    } catch (_) {
      state = const AuthState(
        status: AuthStatus.unauthenticated,
        errorMessage: 'Could not restore session.',
      );
    }
  }

  Future<void> signInPlaceholder() async {
    try {
      final repository = ref.read(authRepositoryProvider);
      final session = await repository.signInPlaceholder();

      state = AuthState(
        status: AuthStatus.authenticated,
        token: session.accessToken,
      );
    } catch (_) {
      state = const AuthState(
        status: AuthStatus.unauthenticated,
        errorMessage: 'Sign in failed. Please try again.',
      );
    }
  }

  Future<void> signOut() async {
    try {
      await ref.read(authRepositoryProvider).signOut();
      state = const AuthState(status: AuthStatus.unauthenticated);
    } catch (_) {
      state = AuthState(
        status: AuthStatus.authenticated,
        token: state.token,
        errorMessage: 'Sign out failed. Please try again.',
      );
    }
  }
}
