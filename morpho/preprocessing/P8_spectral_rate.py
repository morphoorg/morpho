# spectrum_branch-to-high-E.py
#
# T. E. Weiss, 29 August 2019
#
# Purpose:
# Compute fraction of events in beta spectrum that fall near the endpoint.
#


import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import gamma
from scipy import integrate
import random
from scipy.stats import rv_continuous

#Constants
me = 510999.
alpha = 1/137.036
c = 299792458.
hbar = 6.58212*10**(-16)
gv=1.
lambdat = 1.2724 # +/- 0.0023, from PDG (2018): http://pdg.lbl.gov/2018/listings/rpp2018-list-n.pdf
ga=gv*(-lambdat)
Mnuc2 = gv**2 + 3*ga**2
GF =  1.1663787*10**(-23) #Gf/(hc)^3, in eV^(-2)
Vud = 0.97425

#Tritium beta decay-specific constants
QT = 18563.25 #For atomic tritium (eV), from Bodine et al. (2015)
QT2 =  18573.24 #For molecular tritium (eV), Bodine et al. (2015)
Rn =  2.8840*10**(-3) #Helium-3 nuclear radius in units of me, from Kleesiek et al. (2018): https://arxiv.org/pdf/1806.00369.pdf
M = 5497.885 #Helium-3 mass in units of me, Kleesiek et al. (2018)
atomic_num = 2. #For helium-3
g =(1-(atomic_num*alpha)**2)**0.5 #Constant to be used in screening factor and Fermi function calculations
V0 = 76. #Nuclear screening potential of orbital electron cloud of the daughter atom, from Kleesiek et al. (2018)
mu = 5.107 #Difference between magnetic moments of helion and triton, for recoil effects correction


def Ee(K):
    return K+me

def pe(K):
    return math.sqrt(K**2 + 2*K*me)

def beta(K):
    return pe(K)/Ee(K)


#Source for corrections: Kleesiek et al. (2018). According to Table 1, among corrections to the Fermi function, radiative and screening effect have the largest impact on a systematic shift in mnu^2.

#Radiative corretion to the Fermi function (from interactions with real and virtual photons)
def rad_corr(K, Q):
    t = 1./beta(K)*np.arctanh(beta(K))-1
    G = (Q-K)**(2*alpha*t/math.pi)*(1.+2*alpha/math.pi*(t*(math.log(2)-3./2.+(Q-K)/Ee(K))+0.25*(t+1.)*(2.*(1+beta(K)**2)+2*math.log(1-beta(K))+(Q-K)**2/(6*Ee(K)**2))-2+beta(K)/2.-17./36.*beta(K)**2+5./6.*beta(K)**3))
    return G

#Correction for screening by the Coulomb field of the daughter nucleus
def screen_corr(K):
    eta = alpha*atomic_num/beta(K)
    Escreen = Ee(K)-V0
    pscreen = math.sqrt(Escreen**2-me**2)
    etascreen = alpha*atomic_num*Escreen/pscreen
    S = Escreen/Ee(K)*(pscreen/pe(K))**(-1+2*g)*math.exp(math.pi*(etascreen-eta))*(np.absolute(gamma(g+etascreen*1j)))**2/(np.absolute(gamma(g+eta*1j)))**2
    return S

#Correction for exchange with the orbital 1s electron
def exchange_corr(K):
    tau = -2.*alpha/pe(K)
    a = math.exp(2.*tau*np.arctan(-2./tau))*(tau**2/(1+tau**2/4))**2
    I = 1 + 729./256.*a**2 + 27./16.*a
    return I


#Recoil effects (weak magnetism, V-A interference)
def recoil_corr(K, Q):
    A = 2.*(5.*lambdat**2 + lambdat*mu + 1)/M
    B = 2.*lambdat*(mu + lambdat)/M
    C = 1. + 3*lambdat**2 - ((Q+me)/me)*B
    R = 1 + (A*Ee(K)/me - B/(Ee(K)/me))/C
    return R


#Correction for scaling of Coulomb field within daughter nucleus (effect of finite nuclear size) (L)
#Correction for interference of electron/neutrino wavefuction with nucleonic wave function in the nuclear volume (C)
def finite_nuc_corr(K, Q):
    L = 1 + 13./60.*(alpha*atomic_num)**2 - Ee(K)/me*Rn*alpha*atomic_num*(41.-26.*g)/(15.*(2.*g-1.)) - (alpha*atomic_num*Rn*g/(30.*Ee(K)/me))*((17.-2*g)/(2.*g-1.))
    C0 = -233./630.*(alpha*atomic_num)**2 - 1./5.*((Q+me)/me)**2*Rn**2 + 2./35.*(Q+me)/me*Rn*alpha*atomic_num
    C1 = -21./35.*Rn*alpha*atomic_num + 4./9.*(Q+me)/me*Rn**2
    C2 = -4./9.*Rn**2
    C = 1. + C0 + C1*Ee(K)/me + C2*(Ee(K)/me)**2
    return L*C


#Correction for recoiling charge distribution of emitted electron
def coul_corr(K, Q):
    X = 1 - math.pi*alpha*atomic_num/(M*pe(K))*(1.+(1-lambdat**2)/(1+3*lambdat**2)*(Q-K)/(3*Ee(K)))
    return X


#Uncorrected Fermi function for a relativistic electron
def fermi_func(K):
    eta = alpha*atomic_num/beta(K)
    F = 4/(2*pe(K)*Rn)**(2*(1-g))*(np.absolute(gamma(g+eta*1j)))**2/((gamma(2*g+1))**2)*math.exp(math.pi*eta)
    return F

#Electron phase space
def ephasespace(K, Q):
    G = rad_corr(K, Q)         #Radiative correction
    S = screen_corr(K)         #Screening factor
    I = exchange_corr(K)       #Exchange correction
    R = recoil_corr(K, Q)      #Recoil effects
    LC = finite_nuc_corr(K, Q) #Finite nucleus corrections
    X = coul_corr(K, Q)        #Recoiling Coulomb field correction
    F = fermi_func(K)          #Uncorrected Fermi function
    return pe(K)*Ee(K)*F*G*S*I*R*LC*X
    #return 1.


#Tritium beta spectrum
def spectral_rate(K, Q, mnu):
    if K < Q-mnu:
        return GF**2.*Vud**2*Mnuc2/(2.*math.pi**3)*ephasespace(K, Q)*(Q - K)*math.sqrt((Q - K)**2 - (mnu)**2)
        #return GF**2.*Vud**2*Mnuc2/(2.*math.pi**3)*ephasespace(Q-0.001, Q)*(Q - K)*math.sqrt((Q - K)**2 - (mnu)**2) #Fixing electron phase space at value at 1 meV below the endpoint
    else:
        return 0.

def spectral_rate_in_window(K, Q, mnu, Kmin):
    if Q-mnu > K > Kmin:
    #if Q-mnu > K:
        #return GF**2.*Vud**2*Mnuc2/(2.*math.pi**3)*ephasespace(K, Q)*(Q - K)*math.sqrt((Q - K)**2 - (mnu)**2)
        return GF**2.*Vud**2*Mnuc2/(2.*math.pi**3)*ephasespace(K, Q)*((Q - K)**2 - (mnu)**2/2)
        #return GF**2.*Vud**2*Mnuc2/(2.*math.pi**3)*ephasespace(Q-0.001, Q)*(Q - K)*math.sqrt((Q - K)**2 - (mnu)**2) #Fixing electron phase space at value at 1 meV below the endpoint
    else:
        return 0.


def _inverse_approx_spec(K, Q, mnu, deltaE):
    #print(K)
    N = 6/(2*deltaE**3-3*mnu**2*deltaE+mnu**2)
    return 1/(N*((Q - K)**2 - (mnu)**2/2))

def find_inverse_integral(Q, mnu, deltaE):
    x = integrate.quad(_inverse_approx_spec, Q-mnu-deltaE, Q-mnu, args=(Q, mnu, deltaE), epsrel=1e-2, epsabs=0, limit=150)[0]
    #print(x)
    return(1/x)


#print(find_inverse_integral(18563.25, 0.008, 0.11))
#print(find_inverse_integral(18563.25, 0.008, 1))
#print(find_inverse_integral(18563.25, 0.008, 10))




def bkgd_rate_in_window(K, Kmin, Kmax):
    if Kmax > K > Kmin:
        return 1.
    else:
        return 0.

def gaussian(x,a):
    return 1/((2.*math.pi)**0.5*a[1])*(math.exp(-0.5*((x-a[0])/a[1])**2)) 


def _S_integrand(Kp, K, Q, Q_spread, mnu, sigma, Kmin):
    broadening = (sigma**2+Q_spread**2)**0.5
    return spectral_rate_in_window(Kp, Q, mnu, Kmin)*gaussian(Kp, [K, broadening])
    
def _B_integrand(Kp, K, Q_spread, sigma, Kmin, Kmax):
    broadening = (sigma**2+Q_spread**2)**0.5
    return bkgd_rate_in_window(Kp, Kmin, Kmax)*gaussian(Kp, [K, broadening])


def convolved_spectral_rate(K, Q, Q_spread, mnu, sigma, Kmin):
    #Integral bounds chosen to approximately minimize computation error
    pts = []
    broadening = (sigma**2+Q_spread**2)**0.5
    lbound = K-7.*broadening
    ubound = K+7.*broadening
    if lbound<Kmin<ubound:
        pts.append(Kmin)
    if lbound<Q-mnu<ubound:
        pts.append(Q-mnu)
    return integrate.quad(_S_integrand, lbound, ubound, args=(K, Q, Q_spread, mnu, sigma, Kmin), epsrel=1e-2, epsabs=0, limit=150, points=pts)[0]
    

def twonu_convolved_spectral_rate(K, Q, Q_spread, mL, mH, sigma, Kmin, eta):
    return eta*convolved_spectral_rate(K, Q, Q_spread, mL, sigma, Kmin) + (1-eta)*convolved_spectral_rate(K, Q, Q_spread, mH, sigma, Kmin)


def convolved_bkgd_rate(K, Q_spread, sigma, Kmin, Kmax):
    #Integral bounds chosen to approximately minimize computation error
    pts = []
    broadening = (sigma**2+Q_spread**2)**0.5
    lbound = K-7.*broadening
    ubound = K+7.*broadening
    if lbound<Kmin<ubound:
        pts.append(Kmin)
    if lbound<Kmax<ubound:
        pts.append(Kmax)
    return integrate.quad(_B_integrand, lbound, ubound, args=(K, Q_spread, sigma, Kmin, Kmax), epsrel=1e-3, epsabs=0, limit=150, points=pts)[0]


def normalized_signal(K, Q, Q_spread, mnu, sigma, Kmin, Kmax):
    broadening = (sigma**2+Q_spread**2)**0.5
    N = integrate.quad(convolved_spectral_rate, Kmin-7.*broadening, Kmax, args=(Q, Q_spread, mass, sigma, Kmin), epsabs=1e-37, limit=100)[0]
    return convolved_spectral_rate(K, Q, Q_spread, mnu, sigma, Kmin)/N

"""
class signal_prob(rv_continuous): 
""""""Normalized spectral signal disribution.""""""
    def _normalize_signal(self, Q, Q_spread, mnu, sigma, Kmin, Kmax):
        broadening = (sigma**2+Q_spread**2)**0.5
        N = integrate.quad(convolved_spectral_rate, Kmin-7.*broadening, Kmax, args=(Q, Q_spread, mass, sigma, Kmin), epsabs=1e-37, limit=100)[0]
        return N
    def _pdf(self, K, Q, Q_spread, mnu, sigma, Kmin, Kmax, N): 
        return convolved_spectral_rate(K, Q, Q_spread, mnu, sigma, Kmin)/float(N)
"""
"""
mass=0.2
sigma =0.05
KEmax = QT-mass+10.
KEmin = QT-mass-10
Q_spread =0.02
broadening = (sigma**2+Q_spread**2)**0.5
#print(twonu_convolved_spectral_rate(QT, QT, Q_spread, mass, mass, sigma, KEmin, 0.98))
"""
"""
signalp = signal_prob(name = 'signalp', shapes='Q, Q_spread, mnu, sigma, Kmin, Kmax, N', a=KEmin-7.*broadening, b=KEmax)
N = signalp._normalize_signal(QT, Q_spread, mass, sigma, KEmin, KEmax)
print(signalp._pdf(QT-5., QT, Q_spread, mass, sigma, KEmin, KEmax, N))
print(signalp._pdf(QT-1., QT, Q_spread, mass, sigma, KEmin, KEmax, N))
Ks = signalp.rvs(QT, Q_spread, mass, sigma, KEmin, KEmax, N, size=10)
print(Ks)
"""
"""
#print(integrate.quad(spectral_rate_in_window, KEmin-8*sigma, KEmax, args=(QT, mass, KEmin), epsabs=1e-37, limit=100))
print(integrate.quad(twonu_convolved_spectral_rate, KEmin-8*sigma, KEmax, args=(QT, Q_spread, mass, mass, sigma, KEmin, 0.98),  epsabs=1e-37, limit=100))
"""
"""
KE = np.linspace(KEmin-1., KEmax+1., 200)
#plt.plot(KE, [spectral_rate_in_window(K, QT, mass, KEmin) for K in KE], 'b')
#plt.plot(KE, [convolved_spectral_rate(K, QT, Q_spread, mass, sigma, KEmin) for K in KE], 'r')
plt.plot(KE, [bkgd_rate_in_window(K, KEmin, KEmax) for K in KE], 'b')
plt.plot(KE, [convolved_bkgd_rate(K, sigma, KEmin, KEmax) for K in KE], 'r')
plt.xlabel("Kinetic Energy (eV)", fontsize=17)
#plt.ylabel(r"$\beta$ Decay Rate", fontsize=17)
plt.ylabel(r"Background Rate", fontsize=17)
#plt.savefig("zoom_smeared_v_unsmeared_spectra.pdf")
plt.show()
"""

#Fraction of events near the endpoint
def frac_near_endpt(KEmin, Q, mass, atom_or_mol='atom'):
    A = integrate.quad(spectral_rate, KEmin, Q-mass, args=(Q,mass))
    B = integrate.quad(spectral_rate, V0, Q-mass, args=(Q,mass)) #Minimum at V0 because electrons with energy below screening barrier do not escape
    f = (A[0])/(B[0])
    if atom_or_mol=='atom':
        return 0.7006*f
    elif atom_or_mol=='mol' or atom_or_mol=='molecule':
        return 0.57412*f
    else:
        print("Choose 'atom' or 'mol'.")

    

