package com.example.agenticlender

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
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
fun PersonalDetailsScreen(
    onNavigateNext: () -> Unit = {},
    onNavigateBack: () -> Unit = {}
) {
    var firstName by rememberSaveable { mutableStateOf("") }
    var lastName by rememberSaveable { mutableStateOf("") }
    var dob by rememberSaveable { mutableStateOf("") }
    var phone by rememberSaveable { mutableStateOf("") }
    var email by rememberSaveable { mutableStateOf("") }
    var address by rememberSaveable { mutableStateOf("") }
    var householdStatus by rememberSaveable { mutableStateOf("") }
    var dependants by rememberSaveable { mutableStateOf("") }

    var isJointApplication by rememberSaveable { mutableStateOf(false) }
    var coFirstName by rememberSaveable { mutableStateOf("") }
    var coLastName by rememberSaveable { mutableStateOf("") }
    var coEmail by rememberSaveable { mutableStateOf("") }
    var coPhone by rememberSaveable { mutableStateOf("") }
    var coDob by rememberSaveable { mutableStateOf("") }

    var errorMessage by rememberSaveable { mutableStateOf<String?>(null) }
    var successMessage by rememberSaveable { mutableStateOf<String?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(
            text = "1. Personal and Household Details",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            text = "Please provide your personal, contact, and household information.",
            style = MaterialTheme.typography.bodyMedium
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = firstName,
            onValueChange = { firstName = it },
            label = { Text("First Name *") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = lastName,
            onValueChange = { lastName = it },
            label = { Text("Last Name *") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = dob,
            onValueChange = { dob = it },
            label = { Text("Date of Birth (DD/MM/YYYY) *") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = phone,
            onValueChange = { phone = it },
            label = { Text("Phone Number") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email Address") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = address,
            onValueChange = { address = it },
            label = { Text("Home Address") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = householdStatus,
            onValueChange = { householdStatus = it },
            label = { Text("Household Status (e.g., Homeowner, Renter)") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = dependants,
            onValueChange = { dependants = it },
            label = { Text("Number of Dependants") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(8.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(text = "Is this a Joint Application?", style = MaterialTheme.typography.bodyLarge)
            Switch(
                checked = isJointApplication,
                onCheckedChange = { isJointApplication = it }
            )
        }

        if (isJointApplication) {
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Co-Applicant Information",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.secondary
            )
            OutlinedTextField(
                value = coFirstName,
                onValueChange = { coFirstName = it },
                label = { Text("Co-Applicant First Name") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
            OutlinedTextField(
                value = coLastName,
                onValueChange = { coLastName = it },
                label = { Text("Co-Applicant Last Name") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
            OutlinedTextField(
                value = coDob,
                onValueChange = { coDob = it },
                label = { Text("Co-Applicant DOB (DD/MM/YYYY)") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
            OutlinedTextField(
                value = coPhone,
                onValueChange = { coPhone = it },
                label = { Text("Co-Applicant Phone") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
            OutlinedTextField(
                value = coEmail,
                onValueChange = { coEmail = it },
                label = { Text("Co-Applicant Email") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
        }

        if (errorMessage != null) {
            Text(
                text = errorMessage!!,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodyMedium
            )
        }

        if (successMessage != null) {
            Text(
                text = successMessage!!,
                color = MaterialTheme.colorScheme.primary,
                style = MaterialTheme.typography.bodyMedium
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedButton(
                onClick = onNavigateBack,
                modifier = Modifier.weight(1f)
            ) {
                Text("Back")
            }
            Button(
                onClick = {
                    if (firstName.isBlank() || lastName.isBlank() || dob.isBlank() || phone.isBlank() || email.isBlank() || address.isBlank() || householdStatus.isBlank() || dependants.isBlank()) {
                        errorMessage = "Please fill in all required personal and household fields."
                        successMessage = null
                        return@Button
                    }
                    if (isJointApplication && (coFirstName.isBlank() || coLastName.isBlank() || coDob.isBlank() || coPhone.isBlank() || coEmail.isBlank())) {
                        errorMessage = "Please fill in all required co-applicant fields for a joint application."
                        successMessage = null
                        return@Button
                    }
                    errorMessage = null
                    successMessage = "Personal details saved successfully!"
                    onNavigateNext()
                },
                modifier = Modifier.weight(1f)
            ) {
                Text("Save & Continue")
            }
        }
        Spacer(modifier = Modifier.height(24.dp))
    }
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
