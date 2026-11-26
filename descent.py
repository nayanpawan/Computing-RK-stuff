import numpy as np
from rk import solve_ivp
from atmosphere_data import atmospheric_profile
import matplotlib.pyplot as plt

#constants#

m=2000
GM=8.97e12
R=2574e3
Cd=1.2
A=14
x0=12e6
y0=2e6
V=-6.5e3

#diff eq solver for titan orbit/entry physics#

def state_deriv_titan(t, z):

    x = z[0]
    y = z[1]
    vx = z[2]
    vy = z[3]

#calculating variables used in physics model#

    r = np.sqrt(x**2 + y**2)
    h = r - R
    v = np.sqrt(vx**2 + vy**2)
    rho = atmospheric_profile(h)[0]

#decomposing 2 second order into 4 first order ODEs#

    dx = vx
    dy = vy
    dvx = -GM*x/r**3 - 0.5*Cd*A*rho*v*vx/m
    dvy = -GM*y/r**3 - 0.5*Cd*A*rho*v*vy/m

    return np.array([dx, dy, dvx, dvy])

#checks if its hit titan, help reduce sim time for invalid runs#

def hit_titan(t, z):
    r = np.sqrt(z[0]**2 + z[1]**2)
    return r < R


# initial state for a given flight path angle beta
def initial_state(beta):
    return np.array([[x0], [y0], [V*np.cos(beta)], [-V*np.sin(beta)]])


def apoapsis_altitude(beta):
    #solves entire path for a given angle#
    t, z = solve_ivp(state_deriv_titan, 0, 40000, 1, initial_state(beta), stop=hit_titan)
    r = np.sqrt(z[0]**2 + z[1]**2)

    #checking if at end of simu the satelite has crashed#
    if r[-1] < R:
        print(f'  beta = {np.degrees(beta):.4f} deg: crashed')
        return 0

    # finding apoapsis by finding max after periapsis#
    i_peri = np.argmin(r)
    i_apo = i_peri + np.argmax(r[i_peri:])

    #if apoapsis is at end of flight path then either sim time wasn't long enough, crashed or escaped#
    if i_apo == len(r) - 1:
        print(f'  beta = {np.degrees(beta):.4f} deg: apoapsis not reached (escaped or tend too short)')

    return r[i_apo] - R

def find_beta(H, beta0, beta1, tol=1e3, max_iter=20):
    f0 = apoapsis_altitude(beta0) - H
    f1 = apoapsis_altitude(beta1) - H

    for i in range(max_iter):
        if f1 == f0:
            print('secant failed: f1 = f0')
            return beta1

        #secant approximation#
        #approximate between two initial guesses#
        beta2 = beta1 - f1*(beta1 - beta0)/(f1 - f0)
        f2 = apoapsis_altitude(beta2) - H
        print(f'iter {i}: beta = {np.degrees(beta2):.4f} deg, error = {f2/1e3:.3f} km')

        #at end of approx if val under tolerance then return#
        if abs(f2) < tol:
            return beta2

        beta0, f0 = beta1, f1
        beta1, f1 = beta2, f2

    print('did not converge')
    return beta2

def simulate(beta, dt=1, tend=40000):
    t, z = solve_ivp(state_deriv_titan, 0, tend, dt, initial_state(beta), stop=hit_titan)
    return t, z

if __name__ =='__main__':

    H = 9000e3
    prev_beta = None
    prev_apo = 0


    for beta_deg in np.arange(4.88337, 4.88338, 1e-6):
        apo = apoapsis_altitude(np.radians(beta_deg))
        print(f'{beta_deg:.3f} deg -> {apo/1e3:.1f} km')

        #check beta values lead to orbit further from apo stop#
        if apo > H and prev_apo > 0:
            break
        prev_beta = beta_deg
        prev_apo = apo

    beta = find_beta(H, np.radians(prev_beta), np.radians(beta_deg))
    print('beta =', np.degrees(beta), 'deg')

    #checking orbit for specific beta#
    # beta = np.radians(4.883374480677808)

    t, z = solve_ivp(state_deriv_titan, 0, 80000, 1, initial_state(beta), stop=hit_titan)

    plt.figure()
    theta = np.linspace(0, 2*np.pi, 500)
    plt.fill(R*np.cos(theta)/1e3, R*np.sin(theta)/1e3, color='orange', label='Titan')
    plt.plot(z[0]/1e3, z[1]/1e3, label=f'β = {np.degrees(beta):.3f}°')
    plt.axis('equal')
    plt.xlabel('x, km')
    plt.ylabel('y, km')
    plt.legend()
    plt.show()