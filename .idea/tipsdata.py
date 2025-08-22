import pandas as pd
import seaborn as sbn
import matplotlib.pyplot as plt

df = sbn.load_dataset('tips')

days = df.groupby('day')['total_bill'].sum()

print(days)
