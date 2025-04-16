import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import axios from 'axios';

interface GoogleAuthProps {
  mode: 'login' | 'signup';
  userType?: 'user' | 'therapist'; // Required for signup
}

const INTEREST_OPTIONS = [
  'Sports',
  'Reading',
  'Fitness',
  'Cooking',
  'Music',
  'Art',
  'Travel',
  'Technology',
  'Movies',
  'Meditation',
  'Studying',
  'Nature',
];

const SPECIALIZATION_OPTIONS = [
  'Cognitive Behavioral Therapy (CBT)',
  'Depression',
  'Anxiety',
  'Trauma',
  'PTSD',
  'Marriage Counseling',
  'Family Therapy',
  'Addiction',
  'Eating Disorders',
  'Child Psychology',
  'Grief Counseling',
  'Stress Management',
];

const GoogleAuth: React.FC<GoogleAuthProps> = ({ mode, userType }) => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [googleCredential, setGoogleCredential] = useState<string | null>(null);
  const [googleUserData, setGoogleUserData] = useState<any>(null);
  const [showAdditionalForm, setShowAdditionalForm] = useState(false);
  
  // Form state for additional user data
  const [username, setUsername] = useState('');
  const [interests, setInterests] = useState<string[]>([]);
  const [specializations, setSpecializations] = useState<string[]>([]);

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      setError(null);
      const { credential } = credentialResponse;
      
      if (!credential) {
        setError('No credential received from Google. Please try again.');
        return;
      }
      
      // Get the current origin/domain including port
      const currentOrigin = window.location.origin;
      const currentUrl = window.location.href;
      
      console.log('Current origin:', currentOrigin);
      console.log('Current URL:', currentUrl);
      
      // For login, just proceed as before
      if (mode === 'login') {
        const endpoint = 'http://localhost:3000/api/auth/google/login';
        
        // Send the token to the backend along with the current origin for redirect validation
        const response = await axios.post(endpoint, { 
          token: credential,
          redirectUri: currentOrigin,
          currentPage: window.location.pathname
        });
        
        // Store user data in localStorage
        localStorage.setItem('user', JSON.stringify(response.data));
        
        // Redirect to profile page
        navigate('/profile');
      } 
      // For signup, we need to get basic info and then ask for more details
      else if (mode === 'signup' && userType) {
        // Decode the JWT to get basic user info
        try {
          const payload = JSON.parse(atob(credential.split('.')[1]));
          console.log('Decoded Google user data:', payload);
          
          // Save credential and basic user info for later
          setGoogleCredential(credential);
          setGoogleUserData({
            email: payload.email,
            name: payload.name,
            picture: payload.picture
          });
          
          // Show additional form to collect username and interests/specializations
          setShowAdditionalForm(true);
        } catch (decodeError) {
          console.error('Error decoding Google token:', decodeError);
          setError('Could not process Google sign-in data. Please try again.');
        }
      } else {
        setError('Invalid mode or missing userType for signup');
      }
    } catch (error: any) {
      console.error('Google authentication error:', error);
      
      // Check for redirect_uri_mismatch error
      if (error.message?.includes('redirect_uri_mismatch') || 
          error.response?.data?.error === 'redirect_uri_mismatch' ||
          error.response?.data?.message?.includes('redirect')) {
        setError(`Google ${mode} failed: Redirect URI mismatch. Please make sure you've configured the correct redirect URIs in Google Cloud Console.`);
      } else {
        // Display a more user-friendly error message
        const errorMessage = error.response?.data?.message || error.message || 'Authentication failed';
        setError(`Google ${mode} failed: ${errorMessage}`);
      }
    }
  };

  const handleGoogleError = () => {
    console.error('Google sign in was unsuccessful');
    setError('Google sign in was unsuccessful. Please try again or use email/password.');
  };

  const handleInterestChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (e.target.checked) {
      setInterests(prev => [...prev, value]);
    } else {
      setInterests(prev => prev.filter(item => item !== value));
    }
  };

  const handleSpecializationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (e.target.checked) {
      setSpecializations(prev => [...prev, value]);
    } else {
      setSpecializations(prev => prev.filter(item => item !== value));
    }
  };

  const handleAdditionalFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!googleCredential || !googleUserData) {
      setError('Google authentication data is missing. Please try again.');
      return;
    }

    try {
      const currentOrigin = window.location.origin;
      
      // Determine the appropriate endpoint based on userType
      const endpoint = `http://localhost:3000/api/auth/google/signup/${userType}`;
      
      // Prepare payload with all needed data
      const payload = {
        token: googleCredential,
        redirectUri: currentOrigin,
        additionalData: userType === 'user' 
          ? { username, interests } 
          : { username, specializations }
      };
      
      // Send the complete data to backend
      const response = await axios.post(endpoint, payload);
      
      // Store user data in localStorage
      localStorage.setItem('user', JSON.stringify(response.data));
      
      // Redirect to profile page
      navigate('/profile');
    } catch (error: any) {
      console.error('Google signup with additional data error:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Signup failed';
      setError(`Google signup failed: ${errorMessage}`);
    }
  };

  // Check if Google Client ID is configured
  const clientIdMissing = !process.env.REACT_APP_GOOGLE_CLIENT_ID || 
                        process.env.REACT_APP_GOOGLE_CLIENT_ID === 'YOUR_GOOGLE_CLIENT_ID' ||
                        process.env.REACT_APP_GOOGLE_CLIENT_ID === '';

  // If showing the additional data form
  if (showAdditionalForm && googleUserData) {
    return (
      <div className="my-4 border p-4 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-4 text-center">Complete Your Profile</h3>
        
        <div className="flex items-center justify-center mb-4">
          {googleUserData.picture && (
            <img 
              src={googleUserData.picture} 
              alt="Profile" 
              className="w-16 h-16 rounded-full mr-4"
            />
          )}
          <div>
            <p>Email: {googleUserData.email}</p>
            <p>Name from Google: {googleUserData.name}</p>
          </div>
        </div>
        
        {error && (
          <div className="mb-4 text-red-500 text-center text-sm">
            {error}
          </div>
        )}
        
        <form onSubmit={handleAdditionalFormSubmit}>
          <div className="mb-4">
            <label htmlFor="username" className="block mb-2">
              Username <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
              required
              placeholder="Choose a unique username"
            />
            <p className="text-xs text-gray-500 mt-1">
              This username must be unique across all users.
            </p>
          </div>
          
          {userType === 'user' ? (
            <div className="mb-4">
              <label className="block mb-2">
                Interests <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
                {INTEREST_OPTIONS.map((interest) => (
                  <div key={interest}>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="interests"
                        value={interest}
                        checked={interests.includes(interest)}
                        onChange={handleInterestChange}
                        className="mr-2"
                      />
                      {interest}
                    </label>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Select at least one interest.
              </p>
            </div>
          ) : (
            <div className="mb-4">
              <label className="block mb-2">
                Specializations <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
                {SPECIALIZATION_OPTIONS.map((specialization) => (
                  <div key={specialization}>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="specializations"
                        value={specialization}
                        checked={specializations.includes(specialization)}
                        onChange={handleSpecializationChange}
                        className="mr-2"
                      />
                      {specialization}
                    </label>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Select at least one specialization.
              </p>
            </div>
          )}
          
          <div className="flex justify-between">
            <button
              type="button"
              onClick={() => {
                setShowAdditionalForm(false);
                setGoogleCredential(null);
                setGoogleUserData(null);
              }}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 py-2 px-4 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
              disabled={!username || (userType === 'user' ? interests.length === 0 : specializations.length === 0)}
            >
              Complete Signup
            </button>
          </div>
        </form>
      </div>
    );
  }

  // Default Google sign-in button
  return (
    <div className="my-4">
      <div className="flex items-center justify-center mb-2">
        <div className="border-t border-gray-300 flex-grow mr-3"></div>
        <span className="text-gray-500">or</span>
        <div className="border-t border-gray-300 flex-grow ml-3"></div>
      </div>
      
      {error && (
        <div className="mb-4 text-red-500 text-center text-sm">
          {error}
        </div>
      )}

      <div className="flex justify-center">
        {clientIdMissing ? (
          <button 
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded cursor-not-allowed"
            disabled
            title="Google sign-in is not configured"
          >
            {mode === 'login' ? 'Sign in with Google' : 'Sign up with Google'} (Not Configured)
          </button>
        ) : (
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            useOneTap
            theme="filled_blue"
            text={mode === 'login' ? 'signin_with' : 'signup_with'}
            shape="rectangular"
            locale="en"
            context="use"
          />
        )}
      </div>
      
      {clientIdMissing && (
        <p className="mt-2 text-xs text-center text-gray-500">
          Google authentication is not configured. Please set up a Google Client ID in your .env file.
        </p>
      )}
      
      <p className="mt-2 text-xs text-center text-gray-500">
        Current URL: {window.location.href}
      </p>
    </div>
  );
};

export default GoogleAuth; 