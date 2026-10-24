package com.example.agenticlender

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore

@Composable
fun UserDashboard(
    onNavigateToApplication: () -> Unit = {},
    onNavigateToMessages: () -> Unit = {},
    onNavigateToDocuments: () -> Unit = {}
) {
    val auth = remember { FirebaseAuth.getInstance() }
    val db = remember { FirebaseFirestore.getInstance() }
    val currentUser = auth.currentUser

    var fetchedName by remember { mutableStateOf("") }

    LaunchedEffect(currentUser?.uid) {
        currentUser?.uid?.let { uid ->
            db.collection("users").document(uid).get()
                .addOnSuccessListener { document ->
                    if (document.exists()) {
                        val first = document.getString("firstName")
                        val full = document.getString("fullName")
                        fetchedName = when {
                            !first.isNullOrBlank() -> first
                            !full.isNullOrBlank() -> full.substringBefore(" ")
                            else -> currentUser.email?.substringBefore("@")?.replaceFirstChar { it.uppercase() } ?: ""
                        }
                    } else if (currentUser.email != null) {
                        fetchedName = currentUser.email!!.substringBefore("@").replaceFirstChar { it.uppercase() }
                    }
                }
        }
    }

    val displayName = fetchedName.ifBlank { "User" }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Welcome, Header
        Column {
            Text(
                text = "Agentic Lender",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.secondary
            )
            Text(
                text = "Welcome back, $displayName!",
                style = MaterialTheme.typography.headlineLarge,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Here is an overview of your mortgage application progress.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        // Application Progress
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Your Application Progress",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Status: In Progress (%)",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
                Spacer(modifier = Modifier.height(8.dp))
                LinearProgressIndicator(
                    progress = { 0.65f },
                    modifier = Modifier.fillMaxWidth(),
                    color = MaterialTheme.colorScheme.primary,
                    trackColor = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.2f)
                )
                Spacer(modifier = Modifier.height(12.dp))
                Button(
                    onClick = onNavigateToApplication,
                    modifier = Modifier.align(Alignment.End)
                ) {
                    Text(text = "Continue Application")
                }
            }
        }

        // Financial Estimates (Borrowing Capacity & Monthly Repayment)
        ElevatedCard(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Financial Summary",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column {
                        Text(
                            text = "Estimated Borrowing Capacity",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "€",
                            style = MaterialTheme.typography.headlineMedium,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                    }
                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = "Est. Monthly Repayment",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "€ a month",
                            style = MaterialTheme.typography.headlineMedium,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                    }
                }
            }
        }

        // Actions Needed
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.3f)
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Actions Needed",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.error
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "• Upload your latest payslip to verify your current income.",
                    style = MaterialTheme.typography.bodyMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                Button(
                    onClick = onNavigateToDocuments,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    ),
                    modifier = Modifier.align(Alignment.End)
                ) {
                    Text(text = "Upload Documents")
                }
            }
        }

        // 4. Tools and Insights
        Column {
            Text(
                text = "Tools & Insights",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedButton(
                onClick = { /* TODO: Property checker flow */ },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(text = "Property Checker")
            }
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedButton(
                onClick = { /* TODO: AI Results flow */ },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(text = "AI Eligibility & Insights")
            }
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedButton(
                onClick = { /* TODO: Loan Note flow */ },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(text = "View Loan Notes")
            }
        }

        // Recent Message Preview
        OutlinedCard(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Recent Message from Mortgage Broker",
                        style = MaterialTheme.typography.titleSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Badge {
                        Text("1 New")
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "message",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(12.dp))
                Button(
                    onClick = onNavigateToMessages,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(text = "View Messages")
                }
            }
        }
    }
}
