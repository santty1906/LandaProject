import 'app/app_bootstrap.dart';
import 'app/flavor.dart';

Future<void> main() async {
  await bootstrap(flavor: AppFlavor.development);
}
