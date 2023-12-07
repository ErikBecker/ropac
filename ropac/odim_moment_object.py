
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import AxesGrid

import numpy as np

from ropac.config.polar_metadata import DataWhat
from ropac.utils.colours import get_colour_map


class Moment(object):
    def __init__(self):
        self.data = np.array([])
        self.what = DataWhat()
        
    def plot(self):
        
        colour_map = get_colour_map(self.quantity)
        
        missing_color = colour_map['missing']
        underflow_color = colour_map['underflow']  
        overflow_color = colour_map['overflow'] 
        value_min = colour_map['value_min']
        value_max = colour_map['value_max']
        colour = colour_map['colours']
        
        cmap = mpl.colors.ListedColormap(colour)
        
        # Generate sample data
        data = self.get_data()
        
        # Create a figure and a grid of axes using AxesGrid
        fig = plt.figure(figsize=(10, 4))
        grid = AxesGrid(fig, 111, nrows_ncols=(1, 1), axes_pad=0.25, cbar_mode='single', cbar_location='right')

        # Plot the data on the first axis
        # value_max = np.nanmax(data)
        # value_min = np.nanmin(data)
        im = grid[0].imshow(data, cmap=cmap, vmax=value_max, vmin=value_min)
        
        # # Set missing, underflow, and overflow values
        # im.set_bad(missing_color)

        # Create a colorbar on the second axis
        cbar = grid.cbar_axes[0].colorbar(im)
        cbar.ax.tick_params(labelsize=10)

        # Set the title of the colorbar
        cbar.ax.set_title('', fontsize=12)

        # Set the title of the image
        grid[0].set_title(self.quantity, fontsize=12)

        # Show the plot
        plt.show()

    @property
    def quantity(self):
        return self.what.quantity
    
    @property    
    def gain(self):
        return self.what.gain
    
    @property    
    def offset(self):
        return self.what.offset

    def get_data(self):
        return self.data * self.gain + self.offset
    
    
   