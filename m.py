import matplotlib.pyplot as plt
import numpy as np

# Create figure
fig, ax = plt.subplots(figsize=(6, 6))

# Draw axes
ax.axhline(0, color='black', linewidth=1)
ax.axvline(0, color='black', linewidth=1)

# Circle contour C
theta = np.linspace(0, 2*np.pi, 400)
r = 2
x = r * np.cos(theta)
y = r * np.sin(theta)
ax.plot(x, y, label="Contour C (positively oriented)", color='blue')

# Mark a point a outside C
a_x, a_y = 3, 1
ax.plot(a_x, a_y, 'ro', label="Point a (outside C)")

# Mark a point inside C
b_x, b_y = 0.5, 0.5
ax.plot(b_x, b_y, 'go', label="Point inside C")

# Annotate
ax.text(a_x + 0.1, a_y, "a (outside)", color='red')
ax.text(b_x + 0.1, b_y, "inside point", color='green')
ax.text(1.4, 1.4, "C", color='blue', fontsize=12)

# Formatting
ax.set_aspect('equal', adjustable='box')
ax.set_xlabel("Real axis")
ax.set_ylabel("Imaginary axis")
ax.legend()
ax.set_title("Cauchy Integral Formula: a Outside Contour C")
plt.grid(True)
plt.show()
