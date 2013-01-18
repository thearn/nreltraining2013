__all__ = ['ActuatorDisk', 'SmallBEM', 'BEM', 'BladeElement', 'BEMPerf', 'BEMPerfData']

from math import pi, atan2, cos, sin

import numpy as np
from scipy.optimize import fsolve

from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.lib.datatypes.api import Float, Int, Array, Slot
from openmdao.lib.components.api import LinearDistribution


class ActuatorDisk(Component):
    """Simple wind turbine model based on actuator disk theory"""

    #inputs
    a = Float(.5, iotype="in", desc="Induced Velocity Factor", low=0, high=1)
    Area = Float(10, iotype="in", desc="Rotor disk area", units="m**2", low=0)
    rho = Float(1.225, iotype="in", desc="air density", units="kg/m**3")
    Vu = Float(10, iotype="in", desc="Freestream air velocity, upstream of rotor", units="m/s")

    #outputs
    Vr = Float(iotype="out", desc="Air velocity at rotor exit plane", units="m/s")
    Vd = Float(iotype="out", desc="Slipstream air velocity, dowstream of rotor", units="m/s")
    Ct = Float(iotype="out", desc="Thrust Coefficient")
    thrust = Float(iotype="out", desc="Thrust produced by the rotor", units="N")
    Cp = Float(iotype="out", desc="Power Coefficient")
    power = Float(iotype="out", desc="Power produced by the rotor", units="J")

    def execute(self):
        #we use 'a' and 'V0' a lot, so make method local variables

        a = self.a
        Vu = self.Vu

        q = .5*self.rho*self.Area*Vu**2

        self.u1 = Vu*(1-2 * a)
        self.u = .5*(self.Vu + self.Vd)

        self.Ct = 4*a*(1-a)
        self.thrust = self.Ct*q

        self.Cp = self.Ct*(1-a)
        self.power = self.Cp*q*self.Area


class BEMPerfData(VariableTree):
    """Container that holds all rotor performance data"""

    net_thrust = Float(desc="net axial thrust", units="N")
    C_T = Float(desc="thrust coefficient")
    net_torque = Float(desc="net torque", units="N*m")
    C_Q = Float(desc="torque coefficient")
    C_P = Float(desc="power coefficient")
    J = Float(desc="advance ratio")
    eta = Float(desc="turbine efficiency")


class BEMPerf(Component):
    """collects data from set of BladeElements and calculates aggregate values"""

    r = Float(.8, iotype="in", desc="tip radius of the rotor", units="m")
    rpm = Float(2100, iotype="in", desc="rotations per minute", low=0, units="min**-1")
    rho = Float(1.225, iotype="in", desc="air density", units="kg/m**3")
    V_inf = Float(60, iotype="in", desc="free stream air velocity", units="m/s")

    #net_thrust = Float(iotype="out",desc="net axial thrust", units="N")
    #C_T = Float(iotype="out",desc="thrust coefficient")
    #net_torque = Float(iotype="out",desc="net torque", units="N*m")
    #C_P = Float(iotype="out",desc="power coefficient")
    #J = Float(iotype="out",desc="advance ratio")
    #eta = Float(iotype="out",desc="turbine efficiency")

    data = Slot(BEMPerfData, iotype="out")

    #this lets the size of the arrays vary for different numbers of elements
    def __init__(self, n=10):
        super(BEMPerf, self).__init__()
        self.add('data', BEMPerfData())  #needed initialization for VTs
        self.add('delta_T', Array(iotype='in', desc='thrusts from %d different blade elements'%n,
                               default_value=np.ones((n,)), shape=(n,), dtype=Float, units="N"))
        self.add('delta_Q', Array(iotype='in', desc='torques from %d different blade elements'%n,
                               default_value=np.ones((n,)), shape=(n,), dtype=Float, units="N*m"))

    def execute(self):
        self.data = BEMPerfData()  #emtpy the variable tree

        self.data.net_thrust = np.sum(self.delta_T)
        self.data.net_torque = np.sum(self.delta_Q)

        _diam = 2*self.r
        _n = self.rpm/60  #rotations per second
        norm = self.rho*(_n**2)*(_diam**4)

        self.data.C_T = self.data.net_thrust/norm
        self.data.C_Q = self.data.net_torque/(norm*_diam)
        self.data.C_P = self.data.C_Q*2*pi
        self.data.J = self.V_inf/(_n*_diam)
        self.data.eta = self.data.C_T/self.data.C_Q*self.data.J/(2*pi)


class SmallBEM(Assembly):
    """Blade Rotor with 3 BladeElements"""

    #physical properties inputs
    r_hub = Float(0.2, iotype="in", desc="blade hub radius", units="m", low=0)
    twist_hub = Float(61.0, iotype="in", desc="twist angle at the hub radius", units="deg")
    chord_hub = Float(.7, iotype="in", desc="chord length at the rotor hub", units="m", low=.05)
    r_tip = Float(5, iotype="in", desc="blade tip radius", units="m")
    twist_tip = Float(92.58, iotype="in", desc="twist angle at the tip radius", units="deg")
    chord_tip = Float(.187, iotype="in", desc="chord length at the rotor hub", units="m", low=.05)
    pitch = Float(0, iotype="in", desc="overall blade pitch", units="deg")
    rpm = Float(107, iotype="in", desc="rotations per minute", low=0, units="min**-1")
    n_B = Int(3, iotype="in", desc="number of blades", low=1)

    #wind condition inputs
    rho = Float(1.225, iotype="in", desc="air density", units="kg/m**3")
    V_inf = Float(7., iotype="in", desc="free stream air velocity", units="m/s")

    #outputs
    #thrust = Float(iotype="out",desc="net axial thrust", units="N")
    #torque = Float(iotype="out",desc="net torque", units="N*m")
    #J = Float(iotype="out",desc="advance ratio")
    #eta = Float(iotype="out",desc="turbine efficiency")

    #data = Slot(RotorPerfData, iotype="out") #only needed if you do connectio manually

    def configure(self):
        self.add('radius_dist', LinearDistribution(n=3, units="m"))
        self.connect('r_hub', 'radius_dist.start')
        self.connect('r_tip', 'radius_dist.end')

        self.add('chord_dist', LinearDistribution(n=3, units="m"))
        self.connect('chord_hub', 'chord_dist.start')
        self.connect('chord_tip', 'chord_dist.end')

        self.add('twist_dist', LinearDistribution(n=3, units="deg"))
        self.connect('twist_hub', 'twist_dist.start')
        self.connect('twist_tip', 'twist_dist.end')
        self.connect('pitch', 'twist_dist.offset')

        self.driver.workflow.add('radius_dist')
        self.driver.workflow.add('twist_dist')

        self.add('perf', BEMPerf(n=3))
        #self.connect('perf.net_thrust','thrust')
        #self.connect('perf.net_torque','torque')
        #self.connect('perf.J','J')
        #self.connect('perf.eta','eta')
        #self.connect('perf.data','data')
        self.create_passthrough('perf.data')
        self.connect('r_tip', 'perf.r')
        self.connect('rho', 'perf.rho')
        self.connect('rpm', 'perf.rpm')
        self.connect('V_inf', 'perf.V_inf')

        self.add('BE0', BladeElement())
        self.driver.workflow.add('BE0')
        self.BE0.B = 3
        self.connect('radius_dist.output[0]', 'BE0.r')
        self.connect('radius_dist.delta', 'BE0.dr')
        self.connect('twist_dist.output[0]', 'BE0.theta')
        self.connect('chord_dist.output[0]', 'BE0.chord')
        self.connect('rpm', 'BE0.rpm')

        self.connect('rho', 'BE0.rho')
        self.connect('V_inf', 'BE0.V_inf')
        self.connect('BE0.delta_T', 'perf.delta_T[0]')
        self.connect('BE0.delta_Q', 'perf.delta_Q[0]')

        self.add('BE1', BladeElement())
        self.driver.workflow.add('BE1')
        self.BE1.B = 3
        self.connect('radius_dist.output[1]', 'BE1.r')
        self.connect('radius_dist.delta', 'BE1.dr')
        self.connect('twist_dist.output[1]', 'BE1.theta')
        self.connect('chord_dist.output[1]', 'BE1.chord')
        self.connect('rpm', 'BE1.rpm')

        self.connect('rho', 'BE1.rho')
        self.connect('V_inf', 'BE1.V_inf')
        self.connect('BE1.delta_T', 'perf.delta_T[1]')
        self.connect('BE1.delta_Q', 'perf.delta_Q[1]')

        self.add('BE2', BladeElement())
        self.driver.workflow.add('BE2')
        self.BE2.B = 3
        self.connect('radius_dist.output[2]', 'BE2.r')
        self.connect('radius_dist.delta', 'BE2.dr')
        self.connect('twist_dist.output[2]', 'BE2.theta')
        self.connect('chord_dist.output[2]', 'BE2.chord')
        self.connect('rpm', 'BE2.rpm')

        self.connect('rho', 'BE2.rho')
        self.connect('V_inf', 'BE2.V_inf')
        self.connect('BE2.delta_T', 'perf.delta_T[2]')
        self.connect('BE2.delta_Q', 'perf.delta_Q[2]')

        #perf runs last
        self.driver.workflow.add('perf')


class BEM(SmallBEM):
    """Blade Rotor with user specified number BladeElements"""

    def __init__(self, n_elements=6):
        self._n_elements = n_elements
        super(BEM, self).__init__()

    def configure(self):

        n_elements = self._n_elements

        self.add('radius_dist', LinearDistribution(n=n_elements, units="m"))
        self.connect('r_hub', 'radius_dist.start')
        self.connect('r_tip', 'radius_dist.end')

        self.add('chord_dist', LinearDistribution(n=n_elements, units="m"))
        self.connect('chord_hub', 'chord_dist.start')
        self.connect('chord_tip', 'chord_dist.end')

        self.add('twist_dist', LinearDistribution(n=n_elements, units="deg"))
        self.connect('twist_hub', 'twist_dist.start')
        self.connect('twist_tip', 'twist_dist.end')
        self.connect('pitch', 'twist_dist.offset')

        self.driver.workflow.add('radius_dist')
        self.driver.workflow.add('twist_dist')

        self.add('perf', BEMPerf(n=n_elements))
        self.create_passthrough('perf.data')
        self.connect('r_tip', 'perf.r')
        self.connect('rho', 'perf.rho')
        self.connect('rpm', 'perf.rpm')
        self.connect('V_inf', 'perf.V_inf')

        self._elements = []
        for i in range(n_elements):
            name = 'BE%d'%i
            self._elements.append(name)
            self.add(name, BladeElement())
            self.driver.workflow.add(name)
            self.connect('radius_dist.output[%d]'%i, name+'.r')
            self.connect('radius_dist.delta', name+'.dr')
            self.connect('twist_dist.output[%d]'%i, name+'.theta')
            self.connect('chord_dist.output[%d]'%i, name+".chord")
            self.connect('rpm', name+'.rpm')

            self.connect('rho', name+'.rho')
            self.connect('V_inf', name+'.V_inf')
            self.connect(name+'.delta_T', 'perf.delta_T[%d]'%i)
            self.connect(name+'.delta_Q', 'perf.delta_Q[%d]'%i)

        self.driver.workflow.add('perf')

class BladeElement(Component):
    """Calculations for a single radial slice of a rotor blade"""

    #inputs
    a_init = Float(0.2, iotype="in", desc="initial guess for axial inflow factor")
    b_init = Float(0.01, iotype="in", desc="initial guess for angular inflow factor")
    rpm = Float(106.952, iotype="in", desc="rotations per minute", low=0, units="min**-1")
    r = Float(5., iotype="in", desc="mean radius of the blade element", units="m")
    dr = Float(1., iotype="in", desc="width of the blade element", units="m")
    theta = Float(1.616, iotype="in", desc="local pitch angle", units="rad")
    chord = Float(.1872796, iotype="in", desc="local chord length", units="m", low=0)
    B = Int(3, iotype="in", desc="Number of blade elements")

    rho = Float(1.225, iotype="in", desc="air density", units="kg/m**3")
    V_inf = Float(7, iotype="in", desc="free stream air velocity", units="m/s")

    #outputs
    V_0 = Float(iotype="out", desc="axial flow at propeller disk", units="m/s")
    V_1 = Float(iotype="out", desc="local flow velocity", units="m/s")
    V_2 = Float(iotype="out", desc="angular flow at propeller disk", units="m/s")
    omega = Float(iotype="out", desc="average angular velocity for element", units="rad/s")
    sigma = Float(iotype="out", desc="Local solidity")
    alpha = Float(iotype="out", desc="local angle of attack", units="rad")
    delta_T = Float(iotype="out", desc="thrust on the blade element", units="N")
    delta_Q = Float(iotype="out", desc="torque on the blade element", units="N*m")
    a = Float(iotype="out", desc="converged value for axial inflow factor")
    b = Float(iotype="out", desc="converged value for radial inflow factor")
    lambda_r = Float(8, iotype="out", desc="local tip speed ratio")
    phi = Float(1.487, iotype="out", desc="relative flow angle onto blades", units="rad")

    def Coeff_lookup(self, i):
        #piecewise linear interpolation for paper 
        i = self.r
        angles_array_CL = np.array([5., 4., 3., 2., 1., .2][::-1])
        C_L_array = np.array([.6595, .6597, .6589, .6609, .6866, .7][::-1])  

        angles_array_CD = np.array([0,10,20,30,40])
        C_D_array = np.array([0.,0.,0.3,0.6,1.])       

        idx= angles_array_CL.searchsorted(i)-1
        slope =  (C_L_array[idx+1]-C_L_array[idx])/(angles_array_CL[idx+1]-angles_array_CL[idx])
        C_L = slope*(i-angles_array_CL[idx]) + C_L_array[idx]

        idx= angles_array_CD.searchsorted(i)-1
        slope =  (C_D_array[idx+1]-C_D_array[idx])/(angles_array_CD[idx+1]-angles_array_CD[idx])
        C_D = slope*(i-angles_array_CD[idx]) + C_D_array[idx]
        return 0*C_D, C_L
        
        '''#polynomial interpolation from matlab code
        cl=6.2*i
        cd=0.008-0.003*cl+0.01*cl**2
        #return cd, cl
        '''
        '''
        return 0., .7
        '''

    def execute(self):    
        self.sigma = self.B*self.chord / (2* np.pi * self.r)
        self.omega = self.rpm*2*pi/60.0
        omega_r = self.omega*self.r
        self.lambda_r = self.omega*self.r/self.V_inf # need lambda_r for iterates

        #self.a_init = 1./(1 + 4.*(np.cos(1.487)**2)/(self.sigma*0.7*np.sin(1.487)))
        #self.b_init = (1-3*self.a)/(4*self.a - 1)

        self.phi = np.radians(90. - (2/3.)*np.degrees(
            np.arctan(1./self.lambda_r)))

        
        result = fsolve(self.iteration_, [self.a_init, self.b_init])
        self.a = result[0]
        self.b = result[1]

        print self.r, np.degrees(self.theta), np.degrees(self.phi)

        self.V_0 = self.V_inf + self.a*self.V_inf
        self.V_2 = omega_r-self.b*omega_r
        self.V_1 = (self.V_0**2+self.V_2**2)**.5


        q_c = (self.rho*self.V_1**2)*self.chord*self.dr
        cos_phi = cos(self.phi)
        sin_phi = sin(self.phi)
        C_D, C_L = self.Coeff_lookup(self.alpha)
        self.delta_T = q_c*(C_L*cos_phi-C_D*sin_phi)
        self.delta_Q = q_c*self.r*(C_L*sin_phi+C_D*cos_phi)       

    def iteration_(self,X):
        self.phi =  np.arctan(self.lambda_r* (1+X[1]) / (1-X[0]) )
        self.alpha = self.theta - self.phi
        C_D, C_L = self.Coeff_lookup(self.alpha)
        self.a = 1./(1 + 4.*(np.cos(self.phi)**2)/(self.sigma*C_L*np.sin(self.phi)))
        self.b = (self.sigma*C_L) / (4* self.lambda_r * np.cos(self.phi)) * (1 - self.a)

        return (X[0]-self.a), (X[1]-self.b)

if __name__ == "__main__":
    '''
    b = BEM()
    b.run()
    print
    print b.perf.data.C_P
    print b.perf.data.eta
    
    '''
    b = BladeElement()
    b.r= 0.2
    b.gamma = np.radians(61.)
    b.chord = 0.7
    b.run()
    print b.a, b.b
    

