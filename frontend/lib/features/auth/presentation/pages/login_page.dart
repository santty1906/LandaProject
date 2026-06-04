import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../shared/widgets/app_scaffold.dart';
import '../../../../shared/widgets/primary_button.dart';
import '../../application/auth_providers.dart';

class LoginPage extends ConsumerWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);

    return AppScaffold(
      title: 'Login',
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('Authentication placeholder screen'),
          if (authState.errorMessage != null) ...[
            const SizedBox(height: 8),
            Text(
              authState.errorMessage!,
              style: const TextStyle(color: Colors.red),
              textAlign: TextAlign.center,
            ),
          ],
          const SizedBox(height: 16),
          PrimaryButton(
            label: 'Sign in (placeholder)',
            onPressed: () => ref.read(authControllerProvider.notifier).signInPlaceholder(),
          ),
        ],
      ),
    );
  }
}
