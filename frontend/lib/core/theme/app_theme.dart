import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData light() {
    return ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: BankingThemeTokens.primaryBlue,
        primary: BankingThemeTokens.primaryBlue,
        brightness: Brightness.light,
      ),
      useMaterial3: true,
      scaffoldBackgroundColor: BankingThemeTokens.pageBackground,
      cardColor: BankingThemeTokens.surface,
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: BankingThemeTokens.surface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(BankingThemeTokens.fieldRadius),
          borderSide: const BorderSide(color: BankingThemeTokens.inputBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(BankingThemeTokens.fieldRadius),
          borderSide: const BorderSide(color: BankingThemeTokens.inputBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(BankingThemeTokens.fieldRadius),
          borderSide: const BorderSide(color: BankingThemeTokens.primaryBlue, width: 1.2),
        ),
      ),
    );
  }

  static ThemeData dark() {
    return ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: BankingThemeTokens.primaryBlue,
        brightness: Brightness.dark,
      ),
      useMaterial3: true,
    );
  }
}

class BankingThemeTokens {
  static const Color headerRed = Color(0xFFA31920);
  static const Color primaryBlue = Color(0xFF004C8C);
  static const Color accentBlue = Color(0xFF1A73E8);
  static const Color pageBackground = Color(0xFFF3F6FA);
  static const Color surface = Colors.white;
  static const Color inputBorder = Color(0xFFD7DEE8);
  static const Color subtleText = Color(0xFF8B97A8);
  static const Color darkText = Color(0xFF1D2737);
  static const Color glowBlue = Color(0xFFCDEFFF);

  static const double cardRadius = 28;
  static const double fieldRadius = 14;
  static const double actionRadius = 18;

  static const List<BoxShadow> surfaceShadow = [
    BoxShadow(
      color: Color(0x14004C8C),
      blurRadius: 20,
      offset: Offset(0, 8),
    ),
  ];
}
