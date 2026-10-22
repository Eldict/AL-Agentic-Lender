package com.example.agenticlender

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Folder
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.MoreHoriz
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Screen(val route: String) {
    object LandingScreen : Screen("Landing")
    object RegisterScreen : Screen("Register")
    object LoginScreen : Screen("Login")
    object UserDashboard : Screen("UserDashboard")
    object ApplicationScreen : Screen("Application")
    object DocumentsScreen : Screen("Documents")
    object MessageScreen : Screen("Message")
    object MoreScreen : Screen("More")
    object ProfileScreen : Screen("Profile")
    object SettingsScreen : Screen("Settings")
    object HelpScreen : Screen("Help")
    object PaymentScreen : Screen("Payment")
    object PersonalDetailsScreen : Screen("PersonalDetails")
    object EmploymentAndIncomeScreen : Screen("EmploymentAndIncome")
    object DebtsAndAssetsScreen : Screen("DebtsAndAssets")
    object DebtsAndCommitmentsScreen : Screen("DebtsAndCommitments")
    object DepositAndAssetsScreen : Screen("DepositAndAssets")
    object LoanRequestScreen : Screen("LoanRequest")
    object PropertyDetailsScreen : Screen("PropertyDetails")
    object DocumentUploadScreen : Screen("DocumentUpload")
    object ConsentAndDeclarationsScreen : Screen("ConsentAndDeclarations")
}

data class NavItem(
    val label: String,
    val iconId: ImageVector,
    val route: String
)

val navItems = listOf(
    NavItem(label = "Dashboard", iconId = Icons.Default.Home, route = Screen.UserDashboard.route),
    NavItem(label = "Application", iconId = Icons.Default.Description, route = Screen.ApplicationScreen.route),
    NavItem(label = "Documents", iconId = Icons.Default.Folder, route = Screen.DocumentsScreen.route),
    NavItem(label = "Message", iconId = Icons.Default.Email, route = Screen.MessageScreen.route),
    NavItem(label = "More", iconId = Icons.Default.MoreHoriz, route = Screen.MoreScreen.route)
)
