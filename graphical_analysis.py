"""
Created on Sun Nov 20 15:19:01 2022
@author = Karol
"""

# Import Dependencies

import os
import matplotlib.pyplot as plt


"""
Function to take a list of EAR values and plot and save the EAR graph for analysis
"""
def plot_ear_graph(EAR):
    
    try:
        y = list(range(1, len(EAR)+1))
        plt.plot(y, EAR)
        plt.xlabel('Frame')
        plt.ylabel('Average EAR')
        plt.title('EAR for analysis')
        if not os.path.exists("Graphs"):
            print("Creating Graphs Folder !!!")
            os.makedirs("Graphs")
        else:
            print("Graphs Folder already Exists !!!")
        plt.savefig('Graphs/EAR.png', dpi=300, bbox_inches='tight')
        print("EAR Plot saved Successfully !!!")
        return 1
    except:
        print("EAR Plot was not Plot !!!")
        return-1