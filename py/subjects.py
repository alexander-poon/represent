#!/usr/bin/env python

"""
Bill subjects (e.g.: education, health, etc.) are missing for the 111th session. Train
a simple neural network to tag bills with subjects before predicting with topic model.
"""

import pandas as pd
from keras.models import Sequential
from keras.layers import Dense, Dropout
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer

# TODO: Ensure dependency scripts are run before loading
legacy = pd.read_json('data/legacy.json')
current = pd.read_json('data/current.json').drop(columns='subjects')
tokens = pd.read_json('data/tokens.json', typ='series')

tf = TfidfVectorizer(min_df=20, max_df=0.5)
features = tf.fit_transform([' '.join(i) for i in tokens])

# Prediction for sparse classes is hard; select frequent classes
# where it would be helpful to use to apply topic models.
mlb = MultiLabelBinarizer(classes=['Education', 'Health', 'Crime'])
labels = mlb.fit_transform(legacy['subjects'])

# Train/Test Split
train_count = sum(legacy['session'].isin([107, 108, 109]))

X_train = features[:train_count]
Y_train = labels[:train_count]

X_test = features[train_count:len(legacy)]
Y_test = labels[train_count:]

# Train model
model = Sequential()

model.add(Dense(1024, activation='relu', input_dim=X_train.shape[1]))
model.add(Dropout(0.2))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(Y_train.shape[1], activation='sigmoid'))

model.compile(
	loss='binary_crossentropy',
	optimizer='adam',
	metrics=['accuracy']
)

model.fit(X_train, Y_train, epochs=10, batch_size=1500)

test = model.predict(X_test)
test[test >= 0.5] = 1
test[test < 0.5] = 0

# Check Test Accuracy
print('Test Accuracy: ' + str((test == Y_test).mean()))

# Tag 111th bills with subjects
X_pred = features[len(legacy):]

pred = model.predict(X_pred)
pred[pred >= 0.5] = 1
pred[pred < 0.5] = 0

predicted_subjects = pd.Series(mlb.inverse_transform(pred), name='subjects')

print('\nPredicted Subjects:')
print(predicted_subjects.value_counts())

pd.concat([current, predicted_subjects.apply(list)], axis=1) \
	.to_json('data/current.json', orient='records')
