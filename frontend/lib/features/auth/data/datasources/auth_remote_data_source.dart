abstract class AuthRemoteDataSource {
  Future<String> requestPlaceholderToken();
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  @override
  Future<String> requestPlaceholderToken() async {
    return 'placeholder-token';
  }
}
