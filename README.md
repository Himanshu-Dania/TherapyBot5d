# Therapy Connect Application

A web application that connects users with professional therapists. This project is built with a Node.js/Express backend and React/TypeScript frontend.

## Features

- User authentication (signup and login)
- Therapist authentication with document verification
- User interests selection for matching with similar users
- Therapist specialization selection
- Profile management for both user types

## Project Structure

```
├── Backend/             # Node.js/Express backend
│   ├── src/
│   │   ├── config/      # Database configuration
│   │   ├── controllers/ # Request handlers
│   │   ├── middleware/  # Authentication and upload middleware
│   │   ├── models/      # MongoDB schema models
│   │   ├── routes/      # API routes
│   │   └── utils/       # Utility functions
│   ├── server.js        # Main server file
│   └── package.json     # Backend dependencies
│
└── frontend/            # React/TypeScript frontend
    ├── public/          # Static files
    ├── src/
    │   ├── components/  # Reusable UI components
    │   ├── pages/       # Page components
    │   ├── types/       # TypeScript type definitions
    │   ├── App.tsx      # Main app component
    │   └── index.tsx    # Entry point
    └── package.json     # Frontend dependencies
```

## Prerequisites

- Node.js (v14+)
- MongoDB
- npm or yarn

## Setup and Installation

### Backend

1. Navigate to the backend directory:
   ```
   cd Backend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file with the following variables:
   ```
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/therapy_app
   JWT_SECRET=your_jwt_secret_key
   NODE_ENV=development
   ```

4. Start the development server:
   ```
   npm run dev
   ```

### Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. Open your browser and go to `http://localhost:3000`

## API Endpoints

### Users

- `POST /api/users` - Register a new user
- `POST /api/users/login` - Login user
- `GET /api/users/profile` - Get user profile (protected)

### Therapists

- `POST /api/therapists` - Register a new therapist
- `POST /api/therapists/login` - Login therapist
- `GET /api/therapists/profile` - Get therapist profile (protected)

## License

MIT
