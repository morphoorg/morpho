/*
* Tritium Spectrum Model (Generator)
* -----------------------------------------------------
* Copyright: J. A. Formaggio <josephf@mit.edu>
*
* Date: 25 September 2014
*
* Purpose: 
*
*		Program will generate a set of sampled data distributed according to the beta decay spectrum of tritium.
*		Program assumes Project-8 measurement (frequency) and molecular tritium as the source.
*		Spectrum includes Fermi-function correction and final state distribution (assuming 0.36 eV gaussian model)
*		Includes broadening due to magnetic field homogeneity, radiative energy loss, and scattering.
*		T_2 scattering cross-section is assumed constant (18 keV value used) until a better model comes along.
*		Note that sample events are distributed according to true distribution.  
*
*		You can also obtain the number of events (Poisson-distributed) expected as a function of frequency or energy
*		by plotting prob*dy versus frequency or nu versus frequency.
*
*
* Collaboration:  Project 8
*/

functions{

// Set up constants 

	real m_electron() { return  510998.910;}				 // Electron mass in eV
	real c() { return  299792458.;}			   	   	    	 // Speed of light in m/s
	real omega_c() {return 1.758820088e+11;}		         // Angular gyromagnetic ratio in rad Hz/Tesla
	real freq_c() {return omega_c()/(2. * pi());}			 // Gyromagnetic ratio in Hz/Tesla
	real alpha() { return 7.29735257e-3;}               	   	 // Fine structure constant
	real bohr_radius() { return 5.2917721092e-11;}	 	 // Bohr radius in meters
	real k_boltzmann() {return  8.61733238e-5;}		         // Boltzmann's constant in eV/Kelvin
	real unit_mass() { return 931.494061e6;}			 // Unit mass in eV
	real r0_electron() { return square(alpha())*bohr_radius();}  // Electron radius in meters
	real seconds_per_year() {return 365.25 * 86400.;}	         // Seconds in a year

//  Tritium-specific constants

	real tritium_molecular_mass() {return  2. * 3.016 * unit_mass();}   	 // Molecular tritium mass in eV
	real tritium_halflife() {return 12.32 * seconds_per_year();}  // Halflife of tritium (in seconds)
	
// Method for converting kinetic energy (eV) to frequency (Hz).  
// Depends on magnetic field (Tesla)

   	real get_frequency(real kinetic_energy,real field) {
	     real gamma;
	     gamma <- 1. +  kinetic_energy/m_electron();
	     return freq_c() / gamma * field;
	}

// Method for converting frequency (Hz) to kinetic energy (eV)
// Depends on magnetic field (Tesla)

   	real get_kinetic_energy(real frequency, real field) {
	     real gamma;
	     gamma <- freq_c() / frequency * field;
	     return (gamma -1.) * m_electron();
	}

//  Create a centered normal distribution function for faster convergence on normal distributions

	real vnormal_lp(real beta_raw, real mu, real sigma) {
	       beta_raw ~ normal(0,1);
	       return mu + beta_raw * sigma;
	}

//  Create a centered normal distribution function for faster convergence on cauchy distributions.
//  IMPORTANT: The beta_raw input must be distributed within bounds of -pi/2 to +pi/2.

	real vcauchy_lp(real beta_raw, real mu, real sigma) {
	       beta_raw ~ uniform(-pi()/2. , +pi()/2.);
	       return mu +  tan(beta_raw) * sigma;
	}

}

data {

//   Number of neutrinos and mixing parameters

     int<lower=1> nNeutrino;
     simplex[nNeutrino] U_e;
     vector[nNeutrino] m_nu;

//   Primary magnetic field (in Tesla)

     	real<lower=0> BField;
	real BFieldError;

//   Endpoint of tritium, in eV

     	real<lower=0> QValue;
	real QValueError;

//  Cross-section of e-T2 , in meter^-2

     	real<lower=0> eT2_xsection;
     	real eT2_xsectionError;

//  Conditions of the experiment and measurement

	real density;					//  Tritium number density (in meter^-3)
	real temperature;				//  Temperature of gas (in Kelvin)
	real effective_volume;		        //  Effective volume (in meter^3)
	real measuring_time;			//  Measuring time (in seconds)

//  Background rate

	real background_rate;			//  Background rate in Hz

}


transformed data {
	    
        real minKE;
	real maxKE;
	
	vector[nNeutrino] z_nu;
	real signal_rate;

	minKE <- get_kinetic_energy(maxFreq, BField);
	maxKE <- get_kinetic_energy(minFreq, BField);

	z_nu <- m_nu / m_electron();

	signal_rate <- density * effective_volume / (tritium_halflife() / log(2.) );

}


transformed data {

  real<lower=0> beta_max;
  real<lower=0> rad_width;
  real<lower=0> scatt_width;

# Uncertainties assumed in broadening distributions

  sigma_Q <- 0.36;							//  Uncertain in final state distribution (in eV)

  beta_max <-  sqrt(1-square(1. / (1. + Q_value/m_electron)));	   		//  Maximum velocity/(speed of light) of beta decay 
  scatt_width <- cross_section * beta_max * c * density;			    	//  Scattering width in Hertz
  rad_width <- 0.387697196 * square(B);                					//  Free space radiation of particle, tagged at 1 Tesla (in Hz)

}

parameters {
  real y;
  real df;
  real omega;  
  real dQ;
  real eDop;
}

transformed parameters{
  real zmin;
  real eta;
  real nu;
  real beta;
  real nu_doppler;
  real mass_term;
  real tot_width;
  real norm;
  real<lower=0> signal;
  real<lower=0> background;
  real<lower=f_c*ymin, upper=f_c*ymax> f;

  eta <-  1. / (1. + (Q_value+dQ)/m_electron);		
  zmin <- eta +z_nu/square(eta);  
  nu <- ymin + (ymax - ymin) * y;

  beta <- sqrt(1-square(nu));

  nu_doppler <- beta / square(nu) * sqrt(2. * eDop / m_tritium);

  tot_width <- (scatt_width + rad_width);

  mass_term <- sqrt(1.-square((eta * nu * z_nu)/(eta-nu)));

  norm <- (105./(16. *sqrt(2.))) * pow(eta/(1.-eta),3.5) * activity;

  signal <- if_else(nu>zmin && nu<1, norm * beta / pow(nu,6.) * square(nu - eta) / square(eta) * mass_term, 0.);

  background <- background_rate * f_c * time;							

  f <- f_c *(nu + nu_doppler) + (omega + df);
}

model {

 # Dispersion due to uncertainty in final states
  dQ ~ normal(0,sigma_Q);

 # Dispersion due to uncertainty in magnetic field
  df ~ normal(0, f_c *sigma_B / B) ;

 # Dispersion due to frequency broadening
  omega ~ cauchy(0, tot_width); 

  # Thermal Doppler broadening of the tritium source
  eDop ~ gamma(1.5,1./(k_b * temperature));

  # Distribute events uniformly in frequency space.  Make space larger to ensure observable includes tails.
  y ~ uniform(-1.,2.);

 # Generate distribution of events according to beta decay distribution.  Include fermi function correction.
  lp__ <- lp__ + log(signal + background);

  # Apply correction due to neutrino mass being >0 (log Jacobian = log(exp(m_nu)))
  lp__ <- lp__ + m_nu;
}

generated quantities {
  int events;
  real K;

# Compute the number of events that should be simulated for a given frequency/energy.  Assume Poisson distribution.

  events <- poisson_rng((signal + background) * (ymax-ymin));

# Compute the kinetic energy (K) and the measured frequency (f) of each measurement.

  K   <- m_electron * (1.-nu)/nu;

}

