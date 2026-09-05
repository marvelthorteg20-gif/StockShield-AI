import matplotlib

matplotlib.use("TkAgg")   # Force GUI backend

import matplotlib.pyplot as plt

plt.plot([1, 2, 3, 4], [10, 20, 15, 30])
plt.title("Matplotlib Test")
plt.grid(True)

plt.show()