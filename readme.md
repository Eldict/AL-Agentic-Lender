Functionality overview:

This is a small React prototype for an AL Agentic Lender loan-origination pipeline. It lets a user submit a test loan application and view applications stored in Firebase Firestore.

How it works:

App startup: main.jsx mounts the React application into the page’s root element and wraps it in React.StrictMode.
Firebase connection: firebase.js initializes Firebase with the project configuration and exports a Firestore database connection.
Loading applications: App.jsx fetches documents from the Firestore applications collection when the component first loads. Each document is stored in React state and displayed in the pipeline.
Submitting an application: The form collects a borrower name and requested loan amount. On submission, it adds a document to applications with the borrower, loan amount, an initial "Applied" status, and a server-generated timestamp. After a successful write, the form is cleared and the pipeline is fetched again.
Displaying the pipeline: Each application appears with the borrower’s name, requested amount in euros, and status. If there are no applications, the page displays an empty-state message.
The project uses React and Firebase, with Vite for development and production builds, as configured in package.json. The page’s HTML entry point is index.html.

Scope: 
Despite the “Agentic Lender” name, this code currently implements basic application submission and listing. It does not perform loan assessment, update application statuses, or provide authentication. Firebase read/write errors are logged to the browser console.