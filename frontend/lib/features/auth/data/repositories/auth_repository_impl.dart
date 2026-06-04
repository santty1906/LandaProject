import '../../domain/entities/auth_session.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_local_data_source.dart';
import '../datasources/auth_remote_data_source.dart';

class AuthRepositoryImpl implements AuthRepository {
  AuthRepositoryImpl({required this.localDataSource, required this.remoteDataSource});

  final AuthLocalDataSource localDataSource;
  final AuthRemoteDataSource remoteDataSource;

  @override
  Future<AuthSession?> restoreSession() async {
    final token = await localDataSource.readToken();
    if (token == null || token.isEmpty) {
      return null;
    }

    return AuthSession(accessToken: token);
  }

  @override
  Future<AuthSession> signInPlaceholder() async {
    final token = await remoteDataSource.requestPlaceholderToken();
    await localDataSource.saveToken(token);
    return AuthSession(accessToken: token);
  }

  @override
  Future<void> signOut() {
    return localDataSource.clear();
  }
}
