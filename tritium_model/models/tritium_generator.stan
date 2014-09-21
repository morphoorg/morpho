/*
* MC Beta Decay Spectrum Model (Generator)
* -----------------------------------------------------
* Copyright: J. A. Formaggio <josephf@mit.edu>
*
* Date: 7 August 2013
*
* Purpose: 
*
*		Program will generate a set of sampled data distributed according to the beta decay spectrum of tritium.
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

transformed data {

  real n_samples;

  real c;
  real m_electron;
  real m_tritium;
  real alpha;
  real k_b;

  real B;
  real f_c;

  real density;
  real temperature;
  real V_eff;
  real halflife;
  real time;
  real activity;

  real Q_value;
  real<lower=0> t_start;
  real<lower=0> t_end;

  real<lower=0> ymin;
  real<lower=0> ymax;

  real<lower=0> m_nu;
  real<lower=0> z_nu;

  real background_rate;

  real<lower=0> beta_max;
  real<lower=0> cross_section;
  real<lower=0> rad_width;
  real<lower=0> scatt_width;
  real<lower=0> sigma_B;
  real<lower=0> sigma_Q;

# Information about the run itself

  n_samples <- 1000.;

# Fundamental constants to be used in program

  c <- 29979245800;						// Speed of light in cm/s
  m_electron <- 510998.;					// Electron mass in eV
  m_tritium <- 2. * 3.016 * 931.494061e6;		// Tritium molecule mass in eV
  alpha <- 1./137.035999074 ; 			    	// Fine structure constant
  k_b    <- 8.61733238e-5;   				   	// Boltzmann's constant in eV/Kelvin

# Input on magnetic field and cyclotron frequency

  B <- 1.;									// Field strength in Tesla
  f_c <- 27.9924911e+9 * B;     				// Electron cyclotron frequency  in Hertz

# Neutrino mass parameters

   m_nu <- 0.;                                                         // Neutrino mass (in eV)
   z_nu  <- m_nu / m_electron;                               // Normalized neutrino mass

# Start and end energies

  Q_value <- 18575.;						// Endpoint of tritium beta decay spectrum

  t_start <-  0.;   			   	       	   	        // Kinetic energy start for generation
  ymax   <-  1./(1. + t_start/m_electron);

  t_end   <- 18600.;						// Kinetic energy end for generation (includes buffer)
  ymin   <-  1./(1. + t_end/m_electron);

# Calculation of activity for model being used.

  density <- 1.e11;							// tritium number density (in cm^-3)
  temperature <- 30.;						// Temperature of gas (in Kelvin)
  V_eff <- 1.;       							// Effective trapping volume (in cm^3)
  time <- 86400.;            					// Total running time (in seconds)

  halflife <- 12.32 * 31536000.;    				// Tritium half-life in seconds
  activity <- density * V_eff * time / (halflife/log(2.));

# Background calculations.

  background_rate <- 1.e-12;					// Background rate (in events per second per Hz window)

# Uncertainties assumed in broadening distributions

  sigma_Q <- 0.36;							//  Uncertain in final state distribution (in eV)
  sigma_B <- 1.e-05;						//  Uncertainty in magnetic field (in Tesla)

  cross_section <- 3.4e-18;										//  Cross-section of electron-T2 molecule at 18 keV (in cm^2)
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
  real fermi_function;
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

  fermi_function <- (4. * pi() * alpha) / beta/(1.-exp(-(4. * pi() * alpha) / beta)) * (1.002037 - 0.001427 * beta);

  mass_term <- sqrt(1.-square((eta * nu * z_nu)/(eta-nu)));

  norm <- (105./(16. *sqrt(2.))) * pow(eta/(1.-eta),3.5) * activity;

  signal <- if_else(nu>zmin && nu<1, norm * beta / pow(nu,6.) * square(nu - eta) / square(eta) * fermi_function * mass_term, 0.);

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

