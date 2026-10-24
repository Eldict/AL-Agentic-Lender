package com.example.agenticlender

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore

@Composable
fun ProfileScreen(
    onNavigateBack: () -> Unit = {}
) {
    val auth = remember { FirebaseAuth.getInstance() }
    val db = remember { FirebaseFirestore.getInstance() }
    val currentUser = auth.currentUser

    var firstName by remember { mutableStateOf("") }
    var lastName by remember { mutableStateOf("") }
    var email by remember { mutableStateOf(currentUser?.email ?: "") }
    var phone by remember { mutableStateOf("+61 412 345 678") }
    var dob by remember { mutableStateOf("15/08/2000") }
    var address by remember { mutableStateOf("MTU, Bishopstown, Cork, Ireland") }
    var isSaved by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(true) }
    var saveError by remember { mutableStateOf<String?>(null) }

    // user profile from Firestore on load
    LaunchedEffect(currentUser?.uid) {
        currentUser?.uid?.let { uid ->
            db.collection("users").document(uid).get()
                .addOnSuccessListener { document ->
                    if (document.exists()) {
                        val fName = document.getString("firstName")
                        val lName = document.getString("lastName")
                        val full = document.getString("fullName") ?: ""

                        if (!fName.isNullOrBlank()) {
                            firstName = fName
                            lastName = lName ?: ""
                        } else if (full.isNotBlank()) {
                            val parts = full.trim().split(" ", limit = 2)
                            firstName = parts.getOrNull(0) ?: ""
                            lastName = parts.getOrNull(1) ?: ""
                        }

                        email = document.getString("email") ?: (currentUser.email ?: email)
                        phone = document.getString("phone") ?: phone
                        dob = document.getString("dob") ?: dob
                        address = document.getString("address") ?: address
                    }
                    isLoading = false
                }
                .addOnFailureListener {
                    isLoading = false
                }
        } ?: run {
            isLoading = false
        }
    }

    val fullDisplayName = "$firstName $lastName".trim().ifBlank { "User Name" }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Header with Back Button
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onNavigateBack) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back"
                )
            }
            Text(
                text = "My Profile",
                style = MaterialTheme.typography.headlineLarge,
                color = MaterialTheme.colorScheme.primary
            )
        }

        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(32.dp),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            ElevatedCard(
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(64.dp)
                            .clip(CircleShape)
                            .background(MaterialTheme.colorScheme.primaryContainer),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Person,
                            contentDescription = "User Avatar",
                            modifier = Modifier.size(36.dp),
                            tint = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                    Spacer(modifier = Modifier.width(16.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = fullDisplayName,
                            style = MaterialTheme.typography.titleLarge
                        )
                        Text(
                            text = email,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Default.CheckCircle,
                                contentDescription = "Verified",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "Identity Verified",
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }
                    }
                }
            }

            // Personal Information
            Text(
                text = "Personal Information",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = firstName,
                    onValueChange = { firstName = it; isSaved = false },
                    label = { Text("First Name") },
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
                OutlinedTextField(
                    value = lastName,
                    onValueChange = { lastName = it; isSaved = false },
                    label = { Text("Last Name") },
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
            }

            OutlinedTextField(
                value = email,
                onValueChange = { email = it; isSaved = false },
                label = { Text("Email Address") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            OutlinedTextField(
                value = phone,
                onValueChange = { phone = it; isSaved = false },
                label = { Text("Mobile Number") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            OutlinedTextField(
                value = dob,
                onValueChange = { dob = it; isSaved = false },
                label = { Text("Date of Birth") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            OutlinedTextField(
                value = address,
                onValueChange = { address = it; isSaved = false },
                label = { Text("Residential Address") },
                modifier = Modifier.fillMaxWidth()
            )

            if (isSaved) {
                Surface(
                    color = MaterialTheme.colorScheme.primaryContainer,
                    shape = MaterialTheme.shapes.small,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = "Profile updated and saved to Firestore successfully!",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                        modifier = Modifier.padding(12.dp)
                    )
                }
            }

            saveError?.let { error ->
                Surface(
                    color = MaterialTheme.colorScheme.errorContainer,
                    shape = MaterialTheme.shapes.small,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = error,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        modifier = Modifier.padding(12.dp)
                    )
                }
            }

            Button(
                onClick = {
                    currentUser?.uid?.let { uid ->
                        val combinedFullName = "$firstName $lastName".trim()
                        val profileData = hashMapOf(
                            "firstName" to firstName.trim(),
                            "lastName" to lastName.trim(),
                            "fullName" to combinedFullName,
                            "email" to email.trim(),
                            "phone" to phone.trim(),
                            "dob" to dob.trim(),
                            "address" to address.trim(),
                            "updatedAt" to com.google.firebase.Timestamp.now()
                        )
                        db.collection("users").document(uid)
                            .set(profileData, com.google.firebase.firestore.SetOptions.merge())
                            .addOnSuccessListener {
                                isSaved = true
                                saveError = null
                            }
                            .addOnFailureListener { e ->
                                saveError = "Failed to save profile: ${e.localizedMessage}"
                                isSaved = false
                            }
                    } ?: run {
                        saveError = "No authenticated user found."
                    }
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(text = "Save Profile Changes")
            }
        }
    }
}
