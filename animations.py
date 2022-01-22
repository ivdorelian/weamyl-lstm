import matplotlib.pyplot as plt
import numpy as np
from celluloid import Camera

def animate(images, filename):
    fig = plt.figure()
    ax = plt.axes()
    ims = []
    camera = Camera(fig)

    for i, img in enumerate(images):
        im = ax.imshow(img, animated=True)
        if i == 0:
            ax.imshow(img)
        ims.append([im])
        plt.pause(0.1)
        camera.snap()

    animation = camera.animate()
    animation.save(filename, writer='PillowWriter', fps=10)
