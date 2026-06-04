import 'package:flutter/material.dart';

void main() {
  runApp(const LandaApp());
}

class LandaApp extends StatelessWidget {
  const LandaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: Scaffold(
        body: Center(
          child: Text('LandaProject setup in progress'),
        ),
      ),
    );
  }
}
