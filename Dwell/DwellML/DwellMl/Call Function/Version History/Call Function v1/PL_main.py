from lib import *
from lib2 import *
import pandas as pd
import matplotlib.pyplot as plt
import time

data = pd.read_csv("Dataset_ANN.csv")
results = open("results.txt", "w")
timestamp = time.strftime("%Y%m%d-%H%M%S")

Linear_model(data)
plt.savefig(f"Graphs/Linear_model/{timestamp}")
#results.write("Linear Model\n")
#results.write("Linear Model Accuracy: ", acc)

Descion_Tree_model(data)
plt.savefig(f"Graphs/Decision_Tree_Model/{timestamp}")

KNN_Class_model(data)
plt.savefig(f"Graphs/KNN_Class_Model/{timestamp}")

KNN_Reg_model(data)
plt.savefig(f"Graphs/KNN_Reg_Model/{timestamp}")

ANN_model(data)
plt.savefig(f"Graphs/ANN_model/{timestamp}")