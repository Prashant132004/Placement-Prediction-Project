import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
import warnings
warnings.filterwarnings('ignore')

# Load and preprocess data
try:
    df = pd.read_csv('Placement_Prediction_data.csv')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.fillna(0, inplace=True)
    
    # Prepare features and target
    x = df.drop(['StudentId', 'PlacementStatus'], axis=1)
    y = df['PlacementStatus']
    
    # Encode categorical variables
    le = preprocessing.LabelEncoder()
    x['Internship'] = le.fit_transform(x['Internship'])
    x['Hackathon'] = le.fit_transform(x['Hackathon'])
    
    # Split data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=100)
    
    # Train model with updated parameters
    classify = RandomForestClassifier(
        n_estimators=100,
        criterion="entropy",
        random_state=42,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1
    )
    
    # Fit model
    classify.fit(x_train, y_train)
    
    # Make predictions
    ypred = classify.predict(x_test)
    
    # Calculate accuracy
    from sklearn.metrics import accuracy_score
    a = accuracy_score(ypred, y_test)
    print(f"Model Accuracy: {a}")
    
    # Save model
    with open('model.pkl', 'wb') as f:
        pickle.dump(classify, f)
    
    # Test prediction
    test_sample = [[8, 1, 3, 2, 9, 4.8, 0, 1, 71, 87, 0]]
    prediction = classify.predict(test_sample)
    print(f"Test Prediction: {prediction[0]}")
    
except Exception as e:
    print(f"An error occurred: {str(e)}")
