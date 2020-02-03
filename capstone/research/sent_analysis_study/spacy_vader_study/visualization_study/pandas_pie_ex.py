import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

pos = 10.5
neg = 5.7

objects = ('Positive', 'Negative')
y_pos = np.arange(len(objects))
performance = [pos,neg]

plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.ylabel('Sentiment Score')
plt.title('')

plt.savefig('bar.png')
plt.show()