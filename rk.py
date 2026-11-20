import numpy as np
import matplotlib.pyplot as plt

#task 5 msd solver#
def state_deriv_msd(t,z):
    
    m = 2.0    # mass, kg
    c = 0.1    # damping coefficient, N s/m
    k = 0.2    # spring stiffness, N/m

    dz1 = z[1]                           # dx/dt = v
    dz2 = -(c * z[1] + k * z[0]) / m     # dv/dt = -(c v + k x)/m

    dz = np.array([dz1, dz2])
    return dz

#euler method solver#
def step_euler(state_deriv,t,dt,z):

    
    # Euler's update equation
    znext = z + dt * state_deriv(t, z)
    
    return znext

#runge-kutta 4 method solver#

def step_rk(state_deriv,t,dt,z):

    #claculating vals to get znext#
    A= dt*(state_deriv(t,z))
    B= dt*(state_deriv(t+dt/2,z+A/2))
    C= dt*(state_deriv(t+dt/2,z+B/2))
    D= dt*(state_deriv(t+dt,z+C))
    
    znext = z+ (A+2*B+2*C+D)/6
    
    return znext

def solve_ivp(state_deriv,t0,tend,dt,z0,method='RK',stop='none'):
    
    # Set initial conditions
    t = np.array([t0])
    z = z0
    
    # Continue stepping until the end time is exceeded
    n=0
    while t[n] <= tend:
        # Increment by one time step and append to the time axis
        t = np.append(t,t[-1]+dt)
        
        # slecet correct solver
        if method=='RK':
            znext = step_rk(state_deriv,t[n], dt, z[:,n])
        else:
            znext = step_euler(state_deriv,t[n], dt, z[:,n])   
        
        # Append to the solution
        znext = znext[:,np.newaxis]
        z = np.append(z,znext,axis=1)
        
        n = n+1

        if stop is not None and stop(t[n], z[:,n]):
            break
    
    return t, z


if __name__ == '__main__':
    
    # Start time, end time, and time step in seconds
    t0 = 0
    tend = 100
    dt = 0.5
    
    # Initial state in m and m/s
    z0 = np.array([[10],[0]])
    
    # Run the solver
    [t,z] = solve_ivp(state_deriv_msd,t0,tend,dt,z0)
    
    # Plot the result
    plt.close('all')
    plt.figure(1)
    plt.plot(t, z[0,:],'blue')
    plt.plot(t, z[1,:],'red')
    plt.xlabel('Time, s')
    plt.ylabel('State Variables')
    plt.legend(['Displacement, m','Velocity, m/s'])
    plt.show()