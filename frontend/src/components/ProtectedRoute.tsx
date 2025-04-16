import React, { useEffect, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
  userType?: 'user' | 'therapist' | 'any';
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  userType = 'any' 
}) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = () => {
      try {
        const userString = localStorage.getItem('user');
        
        if (!userString) {
          setIsAuthenticated(false);
          return;
        }

        const userData = JSON.parse(userString);
        
        if (!userData || !userData.token) {
          localStorage.removeItem('user');
          setIsAuthenticated(false);
          return;
        }

        setIsAuthenticated(true);

        // Check user type authorization if specified
        if (userType !== 'any') {
          const currentUserType = userData.userType;
          setIsAuthorized(userType === currentUserType);
        } else {
          setIsAuthorized(true);
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        localStorage.removeItem('user');
        setIsAuthenticated(false);
        setIsAuthorized(false);
      }
    };

    checkAuth();
  }, [userType]);

  if (isAuthenticated === null || isAuthorized === null) {
    // Still checking authentication
    return (
      <div className="auth-checking">
        <p>Checking authentication...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!isAuthorized) {
    return (
      <div className="unauthorized">
        <h2>Unauthorized Access</h2>
        <p>You don't have permission to access this page.</p>
        <button onClick={() => navigate(-1)}>Go Back</button>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute; 