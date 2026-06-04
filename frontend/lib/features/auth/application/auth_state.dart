enum AuthStatus { loading, unauthenticated, authenticated }

class AuthState {
  const AuthState({required this.status, this.token, this.errorMessage});

  final AuthStatus status;
  final String? token;
  final String? errorMessage;
}
