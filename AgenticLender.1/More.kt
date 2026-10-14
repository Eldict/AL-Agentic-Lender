package com.example.agenticlender

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun MoreScreen(
    onNavigateToProfile: () -> Unit = {},
    onNavigateToSettings: () -> Unit = {},
    onNavigateToHelp: () -> Unit = {},
    onNavigateToPayment: () -> Unit = {},
    onLogout: () -> Unit = {}
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "{user}", style = MaterialTheme.typography.headlineLarge)
        Text(text = "users email address")
        Button(onClick = onNavigateToProfile) {
            Text(text = "Profile")
        }
        Button(onClick = onNavigateToPayment) {
            Text(text = "Payment")
        }
        Button(onClick = onNavigateToSettings) {
            Text(text = "Settings")
        }
        Button(onClick = onNavigateToHelp) {
            Text(text = "Help")
        }
        Button(onClick = onLogout) {
            Text(text = "Logout")
        }
    }
}

// Screens under More (Profile, Settings, Help, Payment)
@Composable
fun ProfileScreen() {
    Text(text = "Profile Screen")
}

@Composable
fun SettingsScreen() {
    Text(text = "Settings Screen")
}

@Composable
fun HelpScreen() {
    Text(text = "Help Screen")
}

@Composable
fun PaymentScreen() {
    Text(text = "Payment Screen")
}
