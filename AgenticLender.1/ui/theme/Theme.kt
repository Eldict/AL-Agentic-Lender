package com.example.agenticlender.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext

private val AppColorScheme = darkColorScheme(
    primary = PrimaryGreen,
    onPrimary = TextWhite,
    primaryContainer = PrimaryGreen,
    onPrimaryContainer = TextWhite,
    background = DarkGreenBackground,
    onBackground = TextWhite,
    surface = DarkGreenBackground,
    onSurface = TextWhite,
    surfaceVariant = DarkGreenBackground,
    onSurfaceVariant = TextWhite,
    secondary = PrimaryGreen,
    onSecondary = TextWhite,
)

@Composable
fun AgenticLenderTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Set dynamicColor to false so system wallpaper colors don't override your custom theme
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit,
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        else -> AppColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
