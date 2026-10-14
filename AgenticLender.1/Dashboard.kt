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
fun UserDashboard(
    onNavigateToApplication: () -> Unit = {},
    onNavigateToMessages: () -> Unit = {}
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Welcome, {username}", style = MaterialTheme.typography.headlineLarge)
        //show user's dashboard with graphs and charts of their application progress
        //show the currest estimate borrwing capacity
        //show their estimated monthly repayment
        Button(onClick = onNavigateToApplication) {
            Text(text = "Continue to Application ->")
        }
        Text(text = "Tools and Insights")
        Button(onClick = { /*TODO*/ }) {
            Text(text = "Property checker")
        }
        Button(onClick = { /*TODO*/ }) {
            Text(text = "AI Results")
        }
        Button(onClick = { /*TODO*/ }) {
            Text(text = "Loan Note")
        }
        Text(text = "Actions Needed")
        //put a link to anything they need to do like upload the latest payslip
        Text(text = "Recent Message")
        //put a little popup box of an unviewd message
        Button(onClick = onNavigateToMessages) {
            Text(text = "View Messages")
        }
    }
}
