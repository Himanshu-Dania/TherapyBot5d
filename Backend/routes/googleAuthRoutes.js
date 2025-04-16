const express = require('express');
const router = express.Router();
const googleAuthController = require('../controllers/googleAuthController');

// @route   POST /api/auth/google/login
// @desc    Login using Google
// @access  Public
router.post('/login', googleAuthController.googleLogin);

// @route   POST /api/auth/google/signup/user
// @desc    Signup as user using Google
// @access  Public
router.post('/signup/user', googleAuthController.googleSignupUser);

// @route   POST /api/auth/google/signup/therapist
// @desc    Signup as therapist using Google
// @access  Public
router.post('/signup/therapist', googleAuthController.googleSignupTherapist);

module.exports = router; 