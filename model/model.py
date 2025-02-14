import joblib
import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

num_samples = 1000

followers_count = np.random.randint(10, 50000000, num_samples)
following_count = np.random.randint(10, 10000, num_samples)
number_of_posts = np.random.randint(1, 1000, num_samples)


labels = []
for i in range(num_samples):
    if followers_count[i] < 500 and following_count[i] > 2000:  
        labels.append(1)
    elif followers_count[i] > 100000 and number_of_posts[i] < 10:  
        labels.append(1)
    else:
        labels.append(0)  


X = pd.DataFrame({
    "Followers_Count": followers_count,
    "Following_Count": following_count,
    "Number_of_Posts": number_of_posts,
})
y = np.array(labels)  


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


model = SVC(probability=True, kernel='rbf')
model.fit(X_train_scaled, y_train)


joblib.dump(model, "model/model.pkl")
print("Model saved as model/model.pkl")