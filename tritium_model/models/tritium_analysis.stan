/*
* MC Beta Decay Spectrum Model (Analysis)
* -----------------------------------------------------
* Copyright: J. A. Formaggio <josephf@mit.edu>
*
* Date: 12 August 2013
*
* Purpose: 
*
*		Program will analyze a set of sampled data distributed according to the beta decay spectrum of tritium.
*
*		Program assumes Project-8 measurement (frequency) and molecular tritium as the source.
*
*		Spectrum includes Fermi-function correction and final state distribution (assuming 0.36 eV gaussian model)
*
*		Includes broadening due to magnetic field homogeneity, radiative energy loss, and scattering.
*
*		T_2 scattering cross-section is assumed constant (18 keV value used) until a better model comes along.
*
*		Note that sample events are distributed according to true distribution.  
*
*		You can also obtain the number of events (Poisson-distributed) expected as a function of frequency or energy
*		by plotting prob*dy versus frequency or nu versus frequency.
*
*
* Collaboration:  Project 8
*/

data{
	
  int<lower=0> n_samples;
  real<lower=0,upper=1> ymin;
  real<lower=0,upper=1> ymax;
  real frequency[n_samples];

}

transformed data {

  real c;
  real m_electron;
  real m_tritium;
  real alpha;
  real k_b;

  real B;
  real f_c;

  real Q_value;

  real<lower=0> beta_max;
  real<lower=0> cross_section;
  real<lower=0> rad_width;
  real<lower=0> scatt_width;
  real<lower=0> tot_width;
  real<lower=0> sigma_B;
  real<lower=0> sigma_Q;

  real <lower=0> density;
  real <lower=0> temperature;

# Fundamental constants to be used in program

  c <- 29979245800;						// Speed of light in cm/s
  m_electron <- 510998.;					// Electron mass in eV
  m_tritium <- 2. * 3.016 * 931.494061e6;		// Tritium molecule mass in eV
  alpha <- 1./137.035999074 ; 			    	// Fine structure constant
  k_b    <- 8.61733238e-5;   				   	// Boltzmann's constant in eV/Kelvin

# Input on magnetic field and cyclotron frequency

  B <- 1.;									// Field strength in Tesla
  f_c <- 27.9924911e+9 * B;     				// Electron cyclotron frequency  in Hertz

# Start and end energies

  Q_value <- 18575.;						// Endpoint of tritium beta decay spectrum

# Calculation of activity for model being used.

  density <- 1.e11;							// tritium number density (in cm^-3)\  
  temperature <- 30.;						// Temperature of gas (in Kelvin)

# Uncertainties assumed in broadening distributions

  sigma_Q <- 2.00;							//  Constraint in endpoint (in eV)
  sigma_B <- 1.e-05;						//  Uncertainty in magnetic field (in Tesla)

  cross_section <- 3.4e-18;										//  Cross-section of electron-T2 molecule at 18 keV (in cm^2)
  beta_max <-  sqrt(1-square(1. / (1. + Q_value/m_electron)));	   		//  Maximum velocity/(speed of light) of beta decay 
  scatt_width <- cross_section * beta_max * c * density;			    	//  Scattering width in Hertz
  rad_width <- 0.387697196 * square(B);                					//  Free space radiation of particle, tagged at 1 Tesla (in Hz)
  tot_width <- scatt_width + rad_width;

}

parameters {
  real<lower=0> normalization;
  real<lower=0> background;
  real<lower=0> m_nu;
  real<lower=0> endpoint;  

  real y;
  real df;
  real omega;  
  real eDop;
}

transformed parameters{

  real eta;
  real z_nu;
  real nu_min;
  real nu[n_samples];
  real signal[n_samples];
  real beta[n_samples];
  real nu_doppler[n_samples];
  real fermi_function[n_samples];
  real mass_term[n_samples];

  eta <- 1. / (1. + endpoint/m_electron);

  z_nu <- m_nu / m_electron;

  nu_min <- eta + z_nu;

  for (n in 1:n_samples){

    nu[n] <- (frequency[n])/f_c;

    beta[n] <- sqrt(1-square(nu[n]));

    nu_doppler[n] <- beta[n] / square(nu[n]) * sqrt(2. * eDop / m_tritium);

    fermi_function[n] <- (4. * pi() * alpha) / beta[n]/(1.-exp(-(4. * pi() * alpha) / beta[n])) * (1.002037 - 0.001427 * beta[n]);

    mass_term[n] <- sqrt(1.-square((eta * nu[n] * z_nu)/(eta-nu[n])));

    signal[n]<- if_else(nu[n] > nu_min, normalization * beta[n] / pow(nu[n],6.) * square(nu[n] - eta) / square(eta) * fermi_function[n] * mass_term[n], 0.);
  }
}

model {

 # Dispersion due to uncertainty in knowledge of endpoint
  endpoint ~ normal(Q_value,sigma_Q);

 # Dispersion due to uncertainty in magnetic field
  df ~ normal(0, f_c *sigma_B / B) ;

 # Dispersion due to frequency broadening
  omega ~ cauchy(0,tot_width); 

  # Thermal Doppler broadening of the tritium source
  eDop ~ gamma(1.5,1./(k_b * temperature));

   for (n in 1:n_samples) {
        lp__ <- lp__ + log(signal[n] + background);
   }
      
  # Apply correction due to neutrino mass being >0 (log Jacobian = log(exp(m_nu))) ??
  lp__ <- lp__ + m_nu;

}


