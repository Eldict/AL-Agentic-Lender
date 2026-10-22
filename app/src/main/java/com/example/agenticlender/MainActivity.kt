package com.example.agenticlender

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.example.agenticlender.ui.theme.AgenticLenderTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AgenticLenderTheme {
                MainFunction()
            }
        }
    }
}

@Composable
fun MainFunction(modifier: Modifier = Modifier) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    // Show navigation bar only on main bottom tab screens
    val showBottomBar = navItems.any { it.route == currentRoute }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        bottomBar = {
            if (showBottomBar) {
                NavigationBar {
                    navItems.forEach { item ->
                        NavigationBarItem(
                            selected = currentRoute == item.route,
                            onClick = {
                                if (currentRoute != item.route) {
                                    navController.navigate(item.route) {
                                        popUpTo(Screen.UserDashboard.route) {
                                            saveState = true
                                        }
                                        launchSingleTop = true
                                        restoreState = true
                                    }
                                }
                            },
                            icon = {
                                Icon(
                                    imageVector = item.iconId,
                                    contentDescription = item.label
                                )
                            },
                            label = { Text(item.label) }
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.LandingScreen.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.LandingScreen.route) {
                LandingScreen(
                    onNavigateToRegister = { navController.navigate(Screen.RegisterScreen.route) },
                    onNavigateToLogin = { navController.navigate(Screen.LoginScreen.route) }
                )
            }
            composable(Screen.RegisterScreen.route) {
                RegisterScreen(
                    onNavigateToLogin = { navController.navigate(Screen.LoginScreen.route) },
                    onNavigateToCreateAccount = {
                        navController.navigate(Screen.UserDashboard.route) {
                            popUpTo(Screen.LandingScreen.route) { inclusive = true }
                        }
                    }
                )
            }
            composable(Screen.LoginScreen.route) {
                LoginScreen(
                    onNavigateToRegister = { navController.navigate(Screen.RegisterScreen.route) },
                    onNavigateToSignIn = {
                        navController.navigate(Screen.UserDashboard.route) {
                            popUpTo(Screen.LandingScreen.route) { inclusive = true }
                        }
                    }
                )
            }
            composable(Screen.UserDashboard.route) {
                UserDashboard(
                    onNavigateToApplication = { navController.navigate(Screen.ApplicationScreen.route) },
                    onNavigateToMessages = { navController.navigate(Screen.MessageScreen.route) },
                    onNavigateToDocuments = { navController.navigate(Screen.DocumentsScreen.route) }
                )
            }
            composable(Screen.ApplicationScreen.route) {
                ApplicationScreen(
                    onNavigateToPersonalDetails = { navController.navigate(Screen.PersonalDetailsScreen.route) },
                    onNavigateToEmployment = { navController.navigate(Screen.EmploymentAndIncomeScreen.route) },
                    onNavigateToDebtsAndCommitments = { navController.navigate(Screen.DebtsAndCommitmentsScreen.route) },
                    onNavigateToDepositAndAssets = { navController.navigate(Screen.DepositAndAssetsScreen.route) },
                    onNavigateToLoanRequest = { navController.navigate(Screen.LoanRequestScreen.route) },
                    onNavigateToPropertyDetails = { navController.navigate(Screen.PropertyDetailsScreen.route) },
                    onNavigateToUpload = { navController.navigate(Screen.DocumentUploadScreen.route) },
                    onNavigateToConsent = { navController.navigate(Screen.ConsentAndDeclarationsScreen.route) }
                )
            }
            composable(Screen.DocumentsScreen.route) { DocumentsScreen() }
            composable(Screen.MessageScreen.route) { MessageScreen() }
            composable(Screen.MoreScreen.route) {
                MoreScreen(
                    onNavigateToProfile = { navController.navigate(Screen.ProfileScreen.route) },
                    onNavigateToSettings = { navController.navigate(Screen.SettingsScreen.route) },
                    onNavigateToHelp = { navController.navigate(Screen.HelpScreen.route) },
                    onNavigateToPayment = { navController.navigate(Screen.PaymentScreen.route) },
                    onLogout = {
                        navController.navigate(Screen.LandingScreen.route) {
                            popUpTo(Screen.UserDashboard.route) { inclusive = true }
                        }
                    }
                )
            }
            composable(Screen.ProfileScreen.route) { ProfileScreen() }
            composable(Screen.SettingsScreen.route) { SettingsScreen() }
            composable(Screen.HelpScreen.route) { HelpScreen() }
            composable(Screen.PaymentScreen.route) { PaymentScreen() }

            composable(Screen.PersonalDetailsScreen.route) { PersonalDetailsScreen() }
            composable(Screen.EmploymentAndIncomeScreen.route) { EmploymentAndIncomeScreen() }
            composable(Screen.DebtsAndCommitmentsScreen.route) { DebtsAndCommitmentsScreen() }
            composable(Screen.DepositAndAssetsScreen.route) { DepositAndAssetsScreen() }
            composable(Screen.LoanRequestScreen.route) { LoanRequestScreen() }
            composable(Screen.PropertyDetailsScreen.route) { PropertyDetailsScreen() }
            composable(Screen.DocumentUploadScreen.route) { DocumentUploadScreen() }
            composable(Screen.ConsentAndDeclarationsScreen.route) { ConsentAndDeclarationsScreen() }
        }
    }
}
