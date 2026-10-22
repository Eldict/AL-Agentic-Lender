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
        Text(text = "Your answers save automatically, so you can return at any time")
        //show a loading bar of the application progress
        Button(onClick = onNavigateToPersonalDetails) {
            Text(text = "1. Personal and Household Details")
        }
        Button(onClick = onNavigateToEmployment) {
            Text(text = "2. Employment and Income")
        }
        Button(onClick = onNavigateToDebtsAndCommitments) {
            Text(text = "3. Existing Debts and Commitments")
        }
        Button(onClick = onNavigateToDepositAndAssets){
            Text(text = "4. Deposit and Assets")
        }
        Button(onClick = onNavigateToLoanRequest) {
            Text(text = "5. Loan Request")
        }
        Button(onClick = onNavigateToPropertyDetails) {
            Text(text = "6. Property Details")
        }
        Button(onClick = onNavigateToUpload) {
            Text(text = "7. Document Upload Screen")
        }
        Button(onClick = onNavigateToConsent) {
            Text(text = "8. Consent and Declarations")
        }
        //change the number to a check once they have completed it
        //under the headings put complete, in progress or not started
        Text(text = "Your information is secure")
        Text(text = "Protected with bank-level encryption and only visible to authorised viewers")
    }
}

// Loan Application Screens
@Composable
fun PersonalDetailsScreen() {
    Text(text = "Personal Details Screen")
}

@Composable
fun EmploymentAndIncomeScreen() {
    Text(text = "Employment and Income Screen")
}

@Composable
fun DebtsAndCommitmentsScreen() {
    Text(text = "Debts and Commitments Screen")
}

@Composable
fun DepositAndAssetsScreen() {
    Text(text = "Deposit and Assets Screen")
}
@Composable
fun LoanRequestScreen() {
    Text(text = "Loan Request Screen")
}

@Composable
fun PropertyDetailsScreen() {
    Text(text = "Property Details Screen")
}

@Composable
fun DocumentUploadScreen() {
    Text(text = "Document Upload Screen")
}

@Composable
fun ConsentAndDeclarationsScreen() {
    Text(text = "Consent and Declarations Screen")
}




