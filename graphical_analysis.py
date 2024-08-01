__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

# Import Dependencies
import os
import matplotlib.pyplot as plt

def create_graphs_directory():
    """
    Create a directory for saving graphs if it doesn't already exist.
    """
    if not os.path.exists("Graphs"):
        print("Creating 'Graphs' directory...")
        os.makedirs("Graphs")
    else:
        print("'Graphs' directory already exists.")

def plot_ear_graph(EAR):
    """
    Plot and save the Eye Aspect Ratio (EAR) graph for analysis.

    Args:
        EAR (list): List of EAR values to plot.

    Returns:
        int: Returns 1 if the plot is saved successfully, otherwise -1.
    """
    try:
        frames = list(range(1, len(EAR) + 1))
        plt.figure()
        plt.plot(frames, EAR, label='EAR', color='blue')
        plt.xlabel('Frame')
        plt.ylabel('Average EAR')
        plt.title('Eye Aspect Ratio (EAR) Analysis')
        plt.legend()
        
        create_graphs_directory()
        plt.savefig('Graphs/EAR.png', dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free up memory

        print("EAR plot saved successfully.")
        return 1
    except Exception as e:
        print(f"Error saving EAR plot: {e}")
        return -1

def plot_mar_graph(MAR):
    """
    Plot and save the Mouth Aspect Ratio (MAR) graph for analysis.

    Args:
        MAR (list): List of MAR values to plot.

    Returns:
        int: Returns 1 if the plot is saved successfully, otherwise -1.
    """
    try:
        frames = list(range(1, len(MAR) + 1))
        plt.figure()
        plt.plot(frames, MAR, label='MAR', color='red')
        plt.xlabel('Frame')
        plt.ylabel('Average MAR')
        plt.title('Mouth Aspect Ratio (MAR) Analysis')
        plt.legend()
        
        create_graphs_directory()
        plt.savefig('Graphs/MAR.png', dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free up memory

        print("MAR plot saved successfully.")
        return 1
    except Exception as e:
        print(f"Error saving MAR plot: {e}")
        return -1
