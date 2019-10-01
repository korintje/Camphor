
# コメントアウトしているのはmatplotlib使用時のコード
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import seaborn as sns
#%matplotlib inline

sns.set(style='darkgrid', rc={'figure.facecolor':'white'})

df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
#df.plot.line()
df.plot_bokeh.line()
