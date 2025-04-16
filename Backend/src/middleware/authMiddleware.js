const jwt = require('jsonwebtoken');
const User = require('../models/User');
const Therapist = require('../models/Therapist');

const protect = async (req, res, next) => {
  let token;

  if (
    req.headers.authorization &&
    req.headers.authorization.startsWith('Bearer')
  ) {
    try {
      token = req.headers.authorization.split(' ')[1];
      const decoded = jwt.verify(token, process.env.JWT_SECRET);

      // Check if user or therapist
      if (decoded.userType === 'therapist') {
        req.user = await Therapist.findById(decoded.id).select('-password');
      } else {
        req.user = await User.findById(decoded.id).select('-password');
      }

      if (!req.user) {
        return res.status(401).json({ message: 'Not authorized, user not found' });
      }

      next();
    } catch (error) {
      console.error('Auth middleware error:', error.message);
      return res.status(401).json({ 
        message: 'Not authorized, token failed', 
        error: error.message 
      });
    }
  } else {
    return res.status(401).json({ message: 'Not authorized, no token' });
  }
};

module.exports = { protect }; 