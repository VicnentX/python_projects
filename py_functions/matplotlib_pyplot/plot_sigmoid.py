import numpy as np
import matplotlib.pyplot as plt


def sigmoid(t):
    return 1 / (1 + np.exp(-t))


x = np.linspace(-10, 10, 500)
y = sigmoid(x)

print(x.shape)
print(y.shape)

plt.plot(x, y)
plt.show()

