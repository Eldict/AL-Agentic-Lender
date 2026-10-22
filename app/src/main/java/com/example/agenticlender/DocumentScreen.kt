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
fun DocumentsScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Documents", style = MaterialTheme.typography.headlineLarge)
        Text(text = "Upload clear, current copies to keep your application moving forward")
        Button(onClick = { /*TODO*/ }) {
            Text(text = "Upload Document")
        }
        //Documents upload/ to upload
        Button(onClick = { /*TODO*/ }) {
            Text(text = "Proof of Identity")
        }
        Button(onClick = { /*TODO*/ }) {
            Text(text = "Proof of Address")
        }
        Button(onClick = { /*TODO*/ }) {
            Text(text = "latest Payslip")
        }
        Button(onClick = { /*TODO*/ }) {
            Text(text = "Bank Statements")
        }
        Button(onClick = { /*TODO*/ }) {
            Text(text = "Deposit Evidence")
        }
        //have a accepted, uploaded & underreview under each document
    }
}
