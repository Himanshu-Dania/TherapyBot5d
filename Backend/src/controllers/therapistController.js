const Therapist = require('../models/Therapist');
const generateToken = require('../utils/generateToken');
const User = require('../models/User');
const jwt = require('jsonwebtoken');

// @desc    Register a new therapist
// @route   POST /api/therapists
// @access  Public
const registerTherapist = async (req, res, next) => {
  try {
    console.log('Therapist registration request received:', {
      name: req.body.name,
      email: req.body.email,
      hasFile: req.file ? true : false,
      specializations: req.body.specializations
    });

    const { name, username, email, password, specializations } = req.body;
    const file = req.file;
    
    if (!file) {
      console.log('Registration error: No document uploaded');
      return res.status(400).json({ message: 'Please upload a document for verification' });
    }

    console.log('Document details:', {
      originalName: file.originalname,
      mimetype: file.mimetype,
      size: file.size,
      path: file.path
    });

    // Validate required fields
    if (!name || !email || !password) {
      console.log('Registration error: Missing required fields');
      return res.status(400).json({ 
        message: 'Please provide all required fields (name, email, password)' 
      });
    }

    // Check if therapist already exists
    const therapistExists = await Therapist.findOne({ email });
    
    if (therapistExists) {
      console.log('Registration error: Therapist already exists with email', email);
      return res.status(400).json({ message: 'Therapist already exists with this email' });
    }
    
    // Check if username already exists in either collection
    const usernameExists = await Therapist.findOne({ username }) || await User.findOne({ username });
    if (usernameExists) {
      console.log('Registration error: Username already exists', username);
      return res.status(400).json({ message: 'Username is already taken. Please choose another one.' });
    }

    // Check if a user account exists with the same email
    const userExists = await User.findOne({ email });
    if (userExists) {
      console.log('Registration error: A user account exists with email', email);
      return res.status(400).json({ message: 'An account already exists with this email as a user' });
    }

    // Create new therapist
    const therapist = await Therapist.create({
      name,
      username,
      email,
      password,
      specializations: specializations || [],
      document: {
        documentName: file ? file.originalname : '',
        documentPath: file ? file.path : '',
        isVerified: false
      }
    });

    if (therapist) {
      console.log('Therapist registered successfully:', {
        therapistId: therapist._id,
        name: therapist.name,
        email: therapist.email
      });
      
      // Generate JWT token
      const token = jwt.sign(
        { id: therapist._id, email: therapist.email, userType: 'therapist' },
        process.env.JWT_SECRET,
        { expiresIn: '30d' }
      );
      
      res.status(201).json({
        _id: therapist._id,
        name: therapist.name,
        username: therapist.username,
        email: therapist.email,
        document: therapist.document,
        specializations: therapist.specializations,
        userType: 'therapist',
        token: token
      });
    } else {
      console.log('Registration error: Therapist creation failed');
      res.status(400).json({ message: 'Invalid therapist data' });
    }
  } catch (error) {
    console.error('Therapist registration error:', error);
    
    if (error.name === 'ValidationError') {
      return res.status(400).json({ message: error.message });
    }
    
    if (error.code === 11000) {
      return res.status(400).json({ message: 'Duplicate field value entered' });
    }
    
    next(error);
  }
};

// @desc    Auth therapist & get token
// @route   POST /api/therapists/login
// @access  Public
const authTherapist = async (req, res, next) => {
  try {
    const { email, password } = req.body;
    
    if (!email || !password) {
      return res.status(400).json({ message: 'Please provide email and password' });
    }

    const therapist = await Therapist.findOne({ email });

    if (therapist && (await therapist.matchPassword(password))) {
      console.log('Therapist logged in successfully:', {
        therapistId: therapist._id,
        email: therapist.email
      });
      
      res.json({
        _id: therapist._id,
        name: therapist.name,
        email: therapist.email,
        specializations: therapist.specializations,
        userType: therapist.userType,
        document: {
          isVerified: therapist.document.isVerified,
        },
        token: generateToken(therapist._id, therapist.userType),
      });
    } else {
      console.log('Login failed for email:', email);
      res.status(401).json({ message: 'Invalid email or password' });
    }
  } catch (error) {
    console.error('Therapist login error:', error);
    next(error);
  }
};

// @desc    Get therapist profile
// @route   GET /api/therapists/profile
// @access  Private
const getTherapistProfile = async (req, res, next) => {
  try {
    const therapist = await Therapist.findById(req.user._id);

    if (therapist) {
      res.json({
        _id: therapist._id,
        name: therapist.name,
        email: therapist.email,
        specializations: therapist.specializations,
        userType: therapist.userType,
        document: {
          isVerified: therapist.document.isVerified,
        },
      });
    } else {
      res.status(404).json({ message: 'Therapist not found' });
    }
  } catch (error) {
    console.error('Get therapist profile error:', error);
    next(error);
  }
};

module.exports = { registerTherapist, authTherapist, getTherapistProfile }; 