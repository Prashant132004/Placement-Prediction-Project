# Placement Prediction using Machine Learning

This project focuses on predicting student placement and salary in campus recruitment using Random Forest classifiers. The goal is to help students and educational institutions understand the factors that influence placement success and expected salary.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Model Details](#model-details)
- [Web Application](#web-application)
- [Contributing](#contributing)
- [License](#license)

## Overview

Campus placement is a crucial event for students and educational institutions. Predicting placement outcomes and potential salaries can help students prepare better and institutions improve their placement strategies. This project uses Random Forest classifiers to predict both placement probability and expected salary based on various student features.

## Features

- User Authentication System
  - Student Registration and Login
  - Admin Dashboard
  - Secure Password Management
- Placement Prediction
  - Predicts probability of getting placed
  - Considers multiple factors like CGPA, skills, internships, etc.
- Salary Prediction
  - Predicts expected salary for placed students
  - Based on academic performance and other relevant factors
- Admin Dashboard
  - View all registered users
  - Manage user accounts
  - Monitor system usage

## Installation

To run this project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Prashant132004/Placement-Prediction-Project.git
   cd Placement-Prediction-Project
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python init_db.py
   ```

4. Run the application:
   ```bash
   python app.py
   ```

## Project Structure

- `static/`: Contains CSS files and images
  - `css/`: Stylesheets for different pages
  - `images/`: Project images and backgrounds
- `templates/`: Contains HTML templates
  - `admin_dashboard.html`: Admin interface
  - `base.html`: Base template
  - `home.html`: Home page
  - `login.html`: Login page
  - `register.html`: Registration page
- `app.py`: Main Flask application
- `models.py`: Database models
- `model.pkl`: Placement prediction model
- `model1.pkl`: Salary prediction model
- `requirements.txt`: Project dependencies
- `init_db.py`: Database initialization script

## Model Details

### Placement Prediction Model
- Algorithm: Random Forest Classifier
- Accuracy: 88.7%
- Key Features:
  - CGPA
  - Internship Experience
  - Hackathon Participation
  - Technical Skills
  - Communication Skills

### Salary Prediction Model
- Algorithm: Random Forest Regressor
- Features:
  - Academic Performance
  - Work Experience
  - Technical Skills
  - Company Type
  - Job Role

## Web Application

The project includes a full-featured web application built with Flask that provides:
- User registration and authentication
- Placement probability prediction
- Salary prediction
- Admin dashboard for user management
- Responsive design for all devices

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
