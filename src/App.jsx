import React, { useState, useEffect } from 'react';
import { db } from './firebase';
import { collection, addDoc, getDocs, serverTimestamp } from 'firebase/firestore';

export default function App() {
  const [pipeline, setPipeline] = useState([]);
  const [borrower, setBorrower] = useState('');
  const [loanAmount, setLoanAmount] = useState('');

  // Test Read Communication: Fetch centralized queue displaying incoming loan applications[cite: 11]
  const fetchPipeline = async () => {
    try {
      const querySnapshot = await getDocs(collection(db, "applications"));
      const apps = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setPipeline(apps);
    } catch (error) {
      console.error("Error reading from Firebase:", error);
    }
  };

  useEffect(() => {
    fetchPipeline();
  }, []);

  // Test Write Communication: Add an application to the pipeline
  const handleAddApplication = async (e) => {
    e.preventDefault();
    try {
      await addDoc(collection(db, "applications"), {
        borrower: borrower,
        loanRequested: loanAmount,
        status: "Applied",
        timestamp: serverTimestamp()
      });
      setBorrower('');
      setLoanAmount('');
      fetchPipeline(); // Refresh UI to confirm write was successful
    } catch (error) {
      console.error("Error writing to Firebase:", error);
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '800px', margin: 'auto' }}>
      <h1>AL | Agentic Lender Platform</h1>
      <h2 style={{ color: '#555' }}>Origination Pipeline & Firebase Connection Test</h2>
      
      <form onSubmit={handleAddApplication} style={{ background: '#f4f4f9', padding: '1.5rem', borderRadius: '8px', marginBottom: '2rem' }}>
        <h3>Submit Test Application</h3>
        <input 
          type="text" 
          placeholder="Borrower Name" 
          value={borrower} 
          onChange={(e) => setBorrower(e.target.value)} 
          style={{ marginRight: '10px', padding: '0.5rem', width: '200px' }}
          required 
        />
        <input 
          type="number" 
          placeholder="Loan Requested (€)" 
          value={loanAmount} 
          onChange={(e) => setLoanAmount(e.target.value)} 
          style={{ marginRight: '10px', padding: '0.5rem', width: '200px' }}
          required 
        />
        <button type="submit" style={{ padding: '0.5rem 1rem', background: '#4f46e5', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Send to Database
        </button>
      </form>

      <h3>Active Pipeline Volume</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {pipeline.length === 0 ? <p style={{ color: '#888' }}>No applications found. Enter a test application above to verify connection...</p> : null}
        {pipeline.map(app => (
          <li key={app.id} style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '8px', marginBottom: '0.5rem' }}>
            <strong>{app.borrower}</strong> — €{app.loanRequested} 
            <span style={{ float: 'right', background: '#e0e7ff', color: '#3730a3', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.875rem' }}>
              {app.status}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}