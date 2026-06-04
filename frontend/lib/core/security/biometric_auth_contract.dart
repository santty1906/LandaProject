enum BiometricAuthResult { authenticated, failed, unavailable }

abstract class BiometricAuthContract {
  Future<bool> isBiometricAvailable();

  Future<BiometricAuthResult> authenticate({required String reason});
}
