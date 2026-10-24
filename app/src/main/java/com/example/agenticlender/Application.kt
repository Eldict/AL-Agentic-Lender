package com.example.agenticlender

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun ApplicationScreen(
    onNavigateToPersonalDetails: () -> Unit = {},
    onNavigateToEmployment: () -> Unit = {},
    onNavigateToDebtsAndCommitments: () -> Unit = {},
    onNavigateToDepositAndAssets: () -> Unit = {},
    onNavigateToLoanRequest: () -> Unit = {},
    onNavigateToPropertyDetails: () -> Unit = {},
    onNavigateToUpload: () -> Unit = {},
    onNavigateToConsent: () -> Unit = {}
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Your Application", style = MaterialTheme.typography.headlineLarge)
        Text(
            text = "Your answers save automatically, so you can return at any time",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onNavigateToPersonalDetails, modifier = Modifier.fillMaxWidth()) {
            Text(text = "1. Personal and Household Details")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onNavigateToEmployment, modifier = Modifier.fillMaxWidth()) {
            Text(text = "2. Employment and Income")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onNavigateToDebtsAndCommitments, modifier = Modifier.fillMaxWidth()) {
            Text(text = "3. Existing Debts and Commitments")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onNavigateToDepositAndAssets, modifier = Modifier.fillMaxWidth()) {
            Text(text = "4. Deposit and Assets")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onNavigateToLoanRequest, modifier = Modifier.fillMaxWidth()) {
            Text(text = "5. Loan Request")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onNavigateToPropertyDetails, modifier = Modifier.fillMaxWidth()) {
            Text(text = "6. Property Details")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onNavigateToUpload, modifier = Modifier.fillMaxWidth()) {
            Text(text = "7. Document Upload Screen")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onNavigateToConsent, modifier = Modifier.fillMaxWidth()) {
            Text(text = "8. Consent and Declarations")
        }
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Your information is secure",
            style = MaterialTheme.typography.labelLarge
        )
        Text(
            text = "Protected with bank-level encryption and only visible to authorised viewers",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun SubScreenHeader(
    title: String,
    onNavigateBack: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        IconButton(onClick = onNavigateBack) {
            Icon(
                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                contentDescription = "Back"
            )
        }
        Text(
            text = title,
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary
        )
    }
}

// Loan Application Sub-Screens
@Composable
fun PersonalDetailsScreen(onNavigateBack: () -> Unit = {}) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        SubScreenHeader("Personal Details", onNavigateBack)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Personal Details Screen Content")
    }
}

@Composable
fun EmploymentAndIncomeScreen(onNavigateBack: () -> Unit = {}) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        SubScreenHeader("Employment & Income", onNavigateBack)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Employment and Income Screen Content")
    }
}

@Composable
fun DebtsAndCommitmentsScreen(onNavigateBack: () -> Unit = {}) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        SubScreenHeader("Debts & Commitments", onNavigateBack)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Existing Debts and Commitments Screen Content")
    }
}

@Composable
fun DepositAndAssetsScreen(onNavigateBack: () -> Unit = {}) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        SubScreenHeader("Deposit & Assets", onNavigateBack)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Deposit and Assets Screen Content")
    }
}

@Composable
fun LoanRequestScreen(onNavigateBack: () -> Unit = {}) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        SubScreenHeader("Loan Request", onNavigateBack)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Loan Request Screen Content")
    }
}

@Composable
fun PropertyDetailsScreen(onNavigateBack: () -> Unit = {}) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        SubScreenHeader("Property Details", onNavigateBack)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Property Details Screen Content")
    }
}

@Composable
fun DocumentUploadScreen(onNavigateBack: () -> Unit = {}) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        SubScreenHeader("Document Upload", onNavigateBack)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Document Upload Screen Content")
    }
}

@Composable
fun ConsentAndDeclarationsScreen(onNavigateBack: () -> Unit = {}) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        SubScreenHeader("Consent & Declarations", onNavigateBack)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Consent and Declarations Screen Content")
    }
}
