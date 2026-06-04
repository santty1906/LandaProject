import 'package:flutter/material.dart';

import '../../../../shared/widgets/app_scaffold.dart';
import '../../../../shared/widgets/loading_placeholder.dart';

class SplashPage extends StatelessWidget {
  const SplashPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const AppScaffold(
      body: LoadingPlaceholder(message: 'Preparing app...'),
    );
  }
}
