from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.svm import OneClassSVM
import numpy as np
from sklearn.metrics import classification_report
import pandas as pd
import pickle
import warnings
from imblearn.over_sampling import SMOTE, ADASYN
from sklearn.datasets import fetch_openml
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, DetrendOperations
import brainflow
import os
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.svm import OneClassSVM
import numpy as np
from sklearn.metrics import classification_report
import pandas as pd
import pickle
import warnings
from imblearn.over_sampling import SMOTE, ADASYN
from sklearn.datasets import fetch_openml
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
warnings.filterwarnings("ignore")


"""###Read Files, Outlier Elimination, Oversampling"""
dfalpha = pd.read_csv('temp_alphaHigh.csv')
dfalphaLow = pd.read_csv('temp_alphaLow.csv')
dfbeta = pd.read_csv('temp_betaHigh.csv')
dfbetaLow = pd.read_csv('temp_betaLow.csv')
dfgamma = pd.read_csv('temp_gammaHigh.csv')
dfgammaLow = pd.read_csv('temp_gammaLow.csv')
dftheta = pd.read_csv('temp_thetaHigh.csv')
dfthetaLow = pd.read_csv('temp_thetaLow.csv')
frames = [dfalpha, dfalphaLow, dfbeta, dfbetaLow, dfgamma, dfgammaLow, dftheta, dfthetaLow]
df = pd.concat(frames, axis=1)

removeTransitionIndexes = []
for i in range(0, len(df)):
  if df['Direction'][i] == 'Transition':
    removeTransitionIndexes.append(i)
df1 = df.drop(index=removeTransitionIndexes)
df1 = df1.reset_index(drop=True)


start_indexes = [0]
startDir = 'forward'
for i in range(0, len(df1['Direction'])):
  currentDir = df1['Direction'][i]
  if currentDir != startDir:
    start_indexes.append(i)
    startDir = currentDir

df_target = df1['Direction']
df_data = df1.iloc[:, :-1]

Xtrain1, Xtest, ytrain1, ytest = train_test_split(df_data, df_target, test_size=0.35, random_state=42, stratify=df_target)

clf = OneClassSVM(kernel='rbf', nu=0.2, degree=3)
#Outlier remove inside train
shouldRemove = clf.fit_predict(Xtrain1)
index = 0
temp = []
for x in shouldRemove:
  if x == -1:
    temp.append(index)
  index += 1
Xtrain = np.delete(Xtrain1.values, temp, 0)
ytrain = np.delete(ytrain1.values, temp, 0)


#SMOTE oversampling
sm = SMOTE(sampling_strategy='all')
Xtrain, ytrain = sm.fit_resample(Xtrain, ytrain)


def testFit(model):
  yfit = model.predict(Xtest)
  print("TEST PREDICTION")
  print(classification_report(ytest, yfit,
                            target_names=['forward','right','backward','left','stop']))
  a = confusion_matrix(ytest, yfit)
  sns.heatmap(a.T, square=True, annot=True, fmt='d', cbar=False,
            xticklabels=['forward','right','backward','left','stop'], yticklabels=['forward','right','backward','left','stop'])
  plt.show()
  
def trainFit(model):
  print("------------------")
  print("------------------")
  print("------------------")
  print("TRAIN PREDICTION")
  yyfit = model.predict(Xtrain)
  print(classification_report(ytrain, yyfit,
                            target_names=['forward','right','backward','left','stop']))


def fitting(model):
  model.fit(Xtrain, ytrain)
  testFit(model)
  trainFit(model)


"""##MODELS"""
##########################################################################
model_SVM = make_pipeline(StandardScaler(), SVC(gamma='auto'))
param_grid = {'svc__C': [0.1],
              'svc__gamma': [0.1],
              'svc__degree': [2],
              'svc__kernel': ["rbf"]}
grid = GridSearchCV(model_SVM, param_grid)
print("----------------SVM----------------")
fitting(grid)
print("--------------------------------")
print(grid.best_params_)
##########################################################################
##########################################################################
from sklearn.linear_model import LogisticRegression
model_LR = LogisticRegression()
param_grid = {'penalty': ["l1"],
              'C': [1.0],
              'intercept_scaling': [1.2],
              'solver': ["liblinear"]}
grid1 = GridSearchCV(model_LR, param_grid)
print("----------------LogisticRegression----------------")
fitting(grid1)
print("--------------------------------")
print(grid1.best_params_)
##########################################################################
##########################################################################
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
model_LDA = LinearDiscriminantAnalysis()
param_grid = {'store_covariance': [True],
              'n_components': [1],
              'shrinkage': [None],
              'solver': ["lsqr"]}
grid2 = GridSearchCV(model_LDA, param_grid)
print("----------------LinearDiscriminantAnalysis----------------")
fitting(grid2)
print("--------------------------------")
print(grid2.best_params_)
##########################################################################
##########################################################################
from sklearn.ensemble import RandomForestClassifier
model_RFC = RandomForestClassifier(max_depth=2, random_state=0)
param_grid = {'n_estimators': [150],
              'criterion': ["gini"],
              'max_features': ["auto"],
              'verbose': [0]
              }
grid3 = GridSearchCV(model_RFC, param_grid)
print("----------------RandomForestClassifier----------------")
fitting(grid3)
print("--------------------------------")
print(grid3.best_params_)
##########################################################################
##########################################################################
from sklearn.ensemble import GradientBoostingClassifier
model_XGB = GradientBoostingClassifier(n_estimators=100, learning_rate=1,
     max_depth=1, random_state=0)
param_grid = {'n_estimators': [120],
              'loss': ["deviance"],
              'learning_rate': [0.1],
              'verbose': [0]
              }
grid4 = GridSearchCV(model_XGB, param_grid)
print("----------------GradientBoostingClassifier----------------")
fitting(grid4)
print("--------------------------------")
print(grid4.best_params_)
##########################################################################
##########################################################################
from sklearn.naive_bayes import MultinomialNB
model_GNB = MultinomialNB()
param_grid = {'alpha': [0.8, 1.0, 1.2]
              }
grid5 = GridSearchCV(model_GNB, param_grid)
print("----------------MultinomialNB----------------")
fitting(grid5)
print("--------------------------------")
print(grid5.best_params_)
##########################################################################
##########################################################################
from sklearn.tree import DecisionTreeClassifier
model_DTC = DecisionTreeClassifier(random_state=0)
param_grid = {'criterion': ['entropy'],
              'splitter': ['random'],
              'max_depth': [12],
              'min_samples_split': [2]
              }
grid6 = GridSearchCV(model_DTC, param_grid)
print("----------------DecisionTreeClassifier----------------")
fitting(grid6)
print("--------------------------------")
print(grid6.best_params_)
##########################################################################
##########################################################################
from sklearn.neighbors import KNeighborsClassifier
model_KNN = KNeighborsClassifier()
param_grid = {'n_neighbors': [3],
              'weights': ['uniform'],
              'algorithm': ['ball_tree']
              }
grid7 = GridSearchCV(model_KNN, param_grid)
print("----------------KNeighborsClassifier----------------")
fitting(grid7)
print("--------------------------------")
print(grid7.best_params_)
##########################################################################
##########################################################################
from sklearn.ensemble import VotingClassifier
model_voting = VotingClassifier(estimators=[
        ('SVM', grid), ('LR', grid1), ('XGB', grid4)], voting='hard')
print("----------------VotingClassifier----------------")
fitting(model_voting)
print("--------------------------------")
##########################################################################
##########################################################################
filename = 'SVM.sav'
pickle.dump(grid, open(filename, 'wb'))
filename = 'LR.sav'
pickle.dump(grid1, open(filename, 'wb'))
filename = 'LDA.sav'
pickle.dump(grid2, open(filename, 'wb'))
filename = 'RFC.sav'
pickle.dump(grid3, open(filename, 'wb'))
filename = 'XGB.sav'
pickle.dump(grid4, open(filename, 'wb'))
filename = 'MNB.sav'
pickle.dump(grid5, open(filename, 'wb'))
filename = 'DTC.sav'
pickle.dump(grid6, open(filename, 'wb'))
filename = 'KNN.sav'
pickle.dump(grid7, open(filename, 'wb'))
filename = 'VC.sav'
pickle.dump(model_voting, open(filename, 'wb'))