import 'secure_storage.dart';

class AuthSessionStorage {
  AuthSessionStorage(this._secureStorage);

  static const String _tokenKey = 'auth.access_token';

  final SecureStorage _secureStorage;

  Future<void> saveToken(String token) {
    return _secureStorage.write(key: _tokenKey, value: token);
  }

  Future<String?> readToken() {
    return _secureStorage.read(key: _tokenKey);
  }

  Future<void> clear() {
    return _secureStorage.delete(key: _tokenKey);
  }
}
