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


class BladeElement(Component):
    """Calculations for a single radial slice of a rotor blade"""

    #inputs
    a_init = Float(0.1, iotype="in", desc="initial guess for axial inflow factor", low=0, high=1)
    b_init = Float(0.01, iotype="in", desc="initial guess for radial inflow factor", low=0, high=1)
    rpm = Float(2100, iotype="in", desc="rotations per minute", low=0, units="min**-1")
    r = Float(.08, iotype="in", desc="mean radius of the blade element", units="m")
    dr = Float(.072, iotype="in", desc="with of the blade element", units="m")
    theta = Float(1.135, iotype="in", desc="local pitch angle", units="rad", low=0, high=pi/2)
    chord = Float(.1, iotype="in", desc="local chord length", units="m", low=0)

    rho = Float(1.225, iotype="in", desc="air density", units="kg/m**3")
    V_inf = Float(60, iotype="in", desc="free stream air velocity", units="m/s")

    #outputs
    V_0 = Float(iotype="out", desc="axial flow at propeller disk", units="m/s")
    V_1 = Float(iotype="out", desc="local flow velocity", units="m/s")
    V_2 = Float(iotype="out", desc="angular flow at propeller disk", units="m/s")
    omega = Float(iotype="out", desc="average angular velocity for element", units="rad/s")
    alpha = Float(iotype="out", desc="local angle of attack", units="rad")
    delta_T = Float(iotype="out", desc="thrust on the blade element", units="N")
    delta_Q = Float(iotype="out", desc="torque on the blade element", units="N*m")
    a = Float(iotype="out", desc="converged value for axial inflow factor")
    b = Float(iotype="out", desc="converged value for radial inflow factor")

    def execute(self):
        result = fsolve(self._iter_inflow_factor, [self.a_init, self.b_init])
        #result = self._iter_inflow_factor([self.a_init,self.b_init])
        self.a = result[0]
        self.b = result[1]

    def _iter_inflow_factor(self, X):
        """performs one pass through the calculation of inflow factors"""

        a, b = X[0], X[1]
        self.omega = self.rpm*2*pi/60.0
        omega_r = self.omega*self.r

        #using inflow factors, solve for phi and alpha
        self.V_0 = self.V_inf + a*self.V_inf
        self.V_2 = omega_r-b*omega_r
        self.V_1 = (self.V_0**2+self.V_2**2)**.5
        phi = atan2(self.V_0, self.V_2)
        self.alpha = self.theta-phi

        #given alpha, solve for element thrust and torque
        q_c = (self.rho*self.V_1**2)*self.chord*self.dr
        cos_phi = cos(phi)
        sin_phi = sin(phi)
        #C_L = self.alpha*2*pi
        C_L = 6.2*self.alpha
        C_D = 0.008-0.003*C_L+0.01*C_L**2
        self.delta_T = q_c*(C_L*cos_phi-C_D*sin_phi)
        self.delta_Q = q_c*self.r*(C_L*sin_phi+C_D*cos_phi)

        #given thrust and torque, calc new a and b

        const = self.dr*(self.rho*4*pi*self.r)
        #new_a = (-const+(const**2+4*const*self.delta_T)**.5)/(-2*self.delta_T)
        #new_b = self.delta_Q/(const*self.r*self.r*(1+new_a)*self.omega)

        tem1=self.delta_T/(const*(self.V_inf**2)*(1+a))
        tem2=self.delta_Q/(const*(self.r**2)*self.V_inf*(1+a)*self.omega)
        new_a=0.5*(a+tem1)
        new_b=0.5*(b+tem2)

        return (a-new_a, b-new_b)


class BEMPerfData(VariableTree):
    """Container that holds all rotor performance data"""

    net_thrust = Float(desc="net axial thrust", units="N")
    C_T = Float(desc="thrust coefficient")
    net_torque = Float(desc="net torque", units="N*m")
    C_P = Float(desc="power coefficient")
    J = Float(desc="advance ratio")
    eta = Float(desc="turbine efficiency")

class BEMPerf(Component):
    """collects data from set of BladeElements and calculates aggregate values"""

    r = Float(.08, iotype="in", desc="mean radius of the blade element", units="m")
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
        self.data.C_P = self.data.net_torque/(norm*_diam)
        self.data.J = self.V_inf/(_n*_diam)
        self.data.eta = self.data.C_T/self.data.C_P*self.data.J/(2*pi)



class SmallBEM(Assembly):
    """Blade Rotor with 3 BladeElements"""

    #physical properties inputs
    r_hub = Float(0.08, iotype="in", desc="blade hub radius", units="m", low=0)
    twist_hub = Float(65.0, iotype="in", desc="twist angle at the hub radius", units="deg")
    chord_hub = Float(.1, iotype="in", desc="chord length at the rotor hub", units="m", low=.05)
    r_tip = Float(0.8, iotype="in", desc="blade tip radius", units="m")
    twist_tip = Float(25.0, iotype="in", desc="twist angle at the tip radius", units="deg", low=10)
    chord_tip = Float(.1, iotype="in", desc="chord length at the rotor hub", units="m", low=.05)
    pitch = Float(0, iotype="in", desc="overall blade pitch", units="deg")
    rpm = Float(2100, iotype="in", desc="rotations per minute", low=0, units="min**-1")
    n_B = Int(3, iotype="in", desc="number of blades", low=1)

    #wind condition inputs
    rho = Float(1.225, iotype="in", desc="air density", units="kg/m**3")
    V_inf = Float(60, iotype="in", desc="free stream air velocity", units="m/s")

    #outputs
    #thrust = Float(iotype="out",desc="net axial thrust", units="N")
    #torque = Float(iotype="out",desc="net torque", units="N*m")
    #J = Float(iotype="out",desc="advance ratio")
    #eta = Float(iotype="out",desc="turbine efficiency")

    #data = Slot(RotorPerfData, iotype="out") #only needed if you do connectio manually

    def configure(self):
        self.add('radius_dist', LinearDistribution(n=3, units="m"))
        self.connect('r_hub', 'radius_dist.in_0')
        self.connect('r_tip', 'radius_dist.in_1')

        self.add('chord_dist', LinearDistribution(n=3, units="m"))
        self.connect('chord_hub', 'chord_dist.in_0')
        self.connect('chord_tip', 'chord_dist.in_1')

        self.add('twist_dist', LinearDistribution(n=3, units="deg"))
        self.connect('twist_hub', 'twist_dist.in_0')
        self.connect('twist_tip', 'twist_dist.in_1')
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

        self.add('BE0', BladeElement())
        self.driver.workflow.add('BE0')
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

    def __init__(self, n_elements=10):
        self._n_elements = n_elements

    def configure(self):

        n_elements = self._n_elements

        self.add('radius_dist', LinearDistribution(n=n_elements, units="m"))
        self.connect('r_hub', 'radius_dist.in_0')
        self.connect('r_tip', 'radius_dist.in_1')

        self.add('chord_dist', LinearDistribution(n=n_elements, units="m"))
        self.connect('chord_hub', 'chord_dist.in_0')
        self.connect('chord_tip', 'chord_dist.in_1')

        self.add('twist_dist', LinearDistribution(n=n_elements, units="deg"))
        self.connect('twist_hub', 'twist_dist.in_0')
        self.connect('twist_tip', 'twist_dist.in_1')
        self.connect('pitch', 'twist_dist.offset')

        self.driver.workflow.add('radius_dist')
        self.driver.workflow.add('twist_dist')

        self.add('perf', BEMPerf(n=n_elements))
        self.create_passthrough('perf.data')

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
