import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn import preprocessing
import warnings
warnings.filterwarnings('ignore')

# Load and preprocess data
try:
    df = pd.read_csv('Salary_prediction_data.csv')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.fillna(0, inplace=True)
    
    # Prepare features and target
    x = df.drop(['StudentId', 'salary'], axis=1)
    y = df['salary']
    
    # Encode categorical variables
    le = preprocessing.LabelEncoder()
    x['Internship'] = le.fit_transform(x['Internship'])
    x['Hackathon'] = le.fit_transform(x['Hackathon'])
    x['PlacementStatus'] = le.fit_transform(x['PlacementStatus'])
    
    # Split data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=100)
    
    # Train model with updated parameters
    regressor = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1
    )
    
    # Fit model
    regressor.fit(x_train, y_train)
    
    # Make predictions
    ypred = regressor.predict(x_test)
    
    # Calculate R2 score
    from sklearn.metrics import r2_score
    r2 = r2_score(y_test, ypred)
    print(f"Model R2 Score: {r2}")
    
    # Save model
    with open('model1.pkl', 'wb') as f:
        pickle.dump(regressor, f)
    
    # Test prediction
    test_sample = [[8, 1, 3, 2, 9, 4.8, 0, 1, 71, 87, 0, 1]]
    prediction = regressor.predict(test_sample)
    print(f"Test Prediction: {prediction[0]}")
    
except Exception as e:
    print(f"An error occurred: {str(e)}")
