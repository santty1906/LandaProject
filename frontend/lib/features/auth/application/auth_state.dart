enum AuthStatus { loading, unauthenticated, authenticated }

class AuthState {
  const AuthState({required this.status, this.token});

  final AuthStatus status;
  final String? token;
}
