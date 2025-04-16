import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import './App.css';

// Pages
import HomePage from './pages/HomePage';
// @ts-ignore - Suppress TypeScript errors for page imports
import LoginPage from './pages/LoginPage';
// @ts-ignore
import UserSignupPage from './pages/UserSignupPage';
// @ts-ignore
import TherapistSignupPage from './pages/TherapistSignupPage';
// @ts-ignore
import ProfilePage from './pages/ProfilePage';

// Get the Google Client ID from environment variables
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '';
const isValidClientId = GOOGLE_CLIENT_ID && GOOGLE_CLIENT_ID !== 'YOUR_GOOGLE_CLIENT_ID';

const App: React.FC = () => {
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    if (!isValidClientId) {
      console.error('REACT_APP_GOOGLE_CLIENT_ID is not set or invalid. Google authentication will not work.');
      setShowWarning(true);
    }
  }, []);

  return (
    <>
      {showWarning && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          backgroundColor: '#f8d7da',
          color: '#721c24',
          padding: '10px',
          textAlign: 'center',
          zIndex: 1000
        }}>
          ⚠️ Google Client ID is not configured. Google authentication will not work. 
          Please set up a valid client ID in your .env file.
        </div>
      )}
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID || 'dummy-client-id'}>
        <Router>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup/user" element={<UserSignupPage />} />
            <Route path="/signup/therapist" element={<TherapistSignupPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Routes>
        </Router>
      </GoogleOAuthProvider>
    </>
  );
};

export default App;
