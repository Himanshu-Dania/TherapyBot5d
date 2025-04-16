const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const therapistSchema = mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
    },
    username: {
      type: String,
      required: true,
      unique: true,
    },
    email: {
      type: String,
      required: true,
      unique: true,
    },
    password: {
      type: String,
      required: true,
    },
    document: {
      documentName: String,
      documentPath: String,
      isVerified: {
        type: Boolean,
        default: false,
      }
    },
    specializations: [String],
    googleId: {
      type: String,
      sparse: true,
      unique: true,
    },
    profileImage: {
      type: String,
      default: '',
    },
    isGoogleLogin: {
      type: Boolean,
      default: false,
    },
    userType: {
      type: String,
      default: 'therapist',
    }
  },
  {
    timestamps: true,
  }
);

// Hash password before saving
therapistSchema.pre('save', async function (next) {
  if (!this.isModified('password')) {
    next();
  }

  const salt = await bcrypt.genSalt(10);
  this.password = await bcrypt.hash(this.password, salt);
});

// Match therapist password
therapistSchema.methods.matchPassword = async function (enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password);
};

const Therapist = mongoose.model('Therapist', therapistSchema);

module.exports = Therapist; 