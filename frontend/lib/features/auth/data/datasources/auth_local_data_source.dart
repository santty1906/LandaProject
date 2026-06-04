import '../../../../core/storage/auth_session_storage.dart';

abstract class AuthLocalDataSource {
  Future<String?> readToken();

  Future<void> saveToken(String token);

  Future<void> clear();
}

class AuthLocalDataSourceImpl implements AuthLocalDataSource {
  AuthLocalDataSourceImpl(this._storage);

  final AuthSessionStorage _storage;

  @override
  Future<void> clear() {
    return _storage.clear();
  }

  @override
  Future<String?> readToken() {
    return _storage.readToken();
  }

  @override
  Future<void> saveToken(String token) {
    return _storage.saveToken(token);
  }
}
