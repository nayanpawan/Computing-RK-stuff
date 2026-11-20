import numpy as np
from rk import solve_ivp
from atmosphere_data import atmospheric_profile
import matplotlib.pyplot as plt

m=2000
GM=8.97e12
R=2574e3
Cd=1.2
A=14
x0=12e6
y0=2e6
V=-6.5e3

def state_deriv_titan(t, z):

    x = z[0]
    y = z[1]
    vx = z[2]
    vy = z[3]

    r = np.sqrt(x**2 + y**2)
    h = r - R
    v = np.sqrt(vx**2 + vy**2)
    rho = atmospheric_profile(h)[0]

    dx = vx
    dy = vy
    dvx = -GM*x/r**3 - 0.5*Cd*A*rho*v*vx/m
    dvy = -GM*y/r**3 - 0.5*Cd*A*rho*v*vy/m

    return np.array([dx, dy, dvx, dvy])

def hit_titan(t, z):
    r = np.sqrt(z[0]**2 + z[1]**2)
    return r < R


plt.figure()

# draw Titan as a filled orange circle
theta = np.linspace(0, 2*np.pi, 500)
plt.fill(R*np.cos(theta)/1e3, R*np.sin(theta)/1e3, color='orange', label='Titan')

for beta_deg in [10, 30, 45, 60, 80]:
    beta = np.radians(beta_deg)
    z0 = np.array([[x0], [y0], [V*np.cos(beta)], [-V*np.sin(beta)]])

    t, z = solve_ivp(state_deriv_titan, 0, 3000, 0.1, z0, stop=hit_titan)

    plt.plot(z[0]/1e3, z[1]/1e3, label=f'β = {beta_deg}°')

plt.axis('equal')
plt.xlabel('x, km')
plt.ylabel('y, km')
plt.legend()
plt.show()