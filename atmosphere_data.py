import numpy as np
import pandas as pd

# load altitude and density data
data = pd.read_csv('titan_atmosphere.txt', sep=r'\s+')
z0 = data.iloc[:, 0].values
rh0 = data.iloc[:, 1].values

#interpolating function for density#
def atmospheric_profile(z):
    z = np.atleast_1d(z)
    rho = np.zeros(len(z))

#this gives zero density for values outside atmosphere#

    for i in range(len(z)):
        if z[i] >= 0 and z[i] <= z0[-1]:
            rho[i] = np.interp(z[i], z0, rh0)
        else:
            rho[i] = 0

    return np.asarray(rho)



# Test code
if __name__ == '__main__':
    
    # Generate a table
    print('Altitude (m) | Density (kg/m^3)')
    
    # Function accepts single values
    print(f'{-1:12.1e} | {atmospheric_profile(-1).item():.3e}')
    print(f'{0:12.1e} | {atmospheric_profile(0).item():.3e}')
  

    # Function also accepts multiple values as a list or NumPy array
    heights = [0.1,1,10,100,1e3,1e4,1e5,1e6,23e5]
    densities = atmospheric_profile(heights)
    for n, height in enumerate(heights):
        print(f'{height:12.1e} | {densities[n]:.3e}')




    
   