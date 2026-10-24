package com.example.agenticlender.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val DarkColorScheme = darkColorScheme(
    primary = BrightBluePrimary,
    onPrimary = OnBrightBluePrimary,
    primaryContainer = Color(0xFF003853),
    onPrimaryContainer = Color(0xFFCBE7FF),
    secondary = BrightBlueSecondary,
    onSecondary = Color(0xFF000000),
    tertiary = BrightBlueTertiary,
    background = DarkBackground,
    onBackground = Color(0xFFFFFFFF),
    surface = DarkSurface,
    onSurface = Color(0xFFFFFFFF),
    surfaceVariant = DarkSurfaceVariant,
    onSurfaceVariant = Color(0xFFC4C7C5)
)

private val LightColorScheme = lightColorScheme(
    primary = NavyPrimary,
    onPrimary = OnNavyPrimary,
    primaryContainer = Color(0xFFE0F2FE),
    onPrimaryContainer = Color(0xFF0B192C),
    secondary = NavySecondary,
    onSecondary = Color(0xFFFFFFFF),
    tertiary = NavyTertiary,
    background = LightBackground,
    onBackground = Color(0xFF0B192C),
    surface = LightSurface,
    onSurface = Color(0xFF0B192C),
    surfaceVariant = LightSurfaceVariant,
    onSurfaceVariant = Color(0xFF444746)
)

@Composable
fun AgenticLenderTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        (dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }

        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
