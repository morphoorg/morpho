/*
* Tritium Spectrum Model (Analysis)
* -----------------------------------------------------
* Copyright: J. A. Formaggio <josephf@mit.edu>
*
* Date: 25 March 2015
*
* Purpose: 
*
*		Program will analyze a set of generated data distributed according to the beta decay spectrum of tritium.
*		Program assumes Project-8 measurement (frequency) and molecular tritium as the source.
*		Spectrum includes simplified beta-function with final state distribution (assuming 0.36 eV gaussian model)
*		Includes broadening due to magnetic field homogeneity, radiative energy loss, Doppler and scattering.
*		T_2 scattering cross-section model implemented.
*		Note that sample events are distributed according to true distribution.  
*
*
* Collaboration:  Project 8
*/

functions{

// Set up constants 

	real m_electron() { return  510998.910;}				// Electron mass in eV
	real c() { return  299792458.;}			   	   	 	// Speed of light in m/s
	real omega_c() {return 1.758820088e+11;}		         	// Angular gyromagnetic ratio in rad Hz/Tesla
	real freq_c() {return omega_c()/(2. * pi());}			 	// Gyromagnetic ratio in Hz/Tesla
	real alpha() { return 7.29735257e-3;}               	   	 	// Fine structure constant
	real bohr_radius() { return 5.2917721092e-11;}	 	 	 	// Bohr radius in meters
	real k_boltzmann() {return  8.61733238e-5;}		         	// Boltzmann's constant in eV/Kelvin
	real unit_mass() { return 931.494061e6;}			 	// Unit mass in eV
	real r0_electron() { return square(alpha())*bohr_radius();}  	 	// Electron radius in meters
	real ry_hydrogen() { return 13.60569253;}                    	    	// Rydberg energy in eV
	real cyclotron_rad(real B) {return (4./3.)*r0_electron()/c()*square(omega_c() * B);}    // Frequency damping constant (in units of Hz/Tesla^2)
	real seconds_per_year() {return 365.25 * 86400.;}	        	// Seconds in a year

//  Tritium-specific constants

    	real tritium_rate_per_eV() {return 2.0e-13;}				 // fraction of rate in last 1 eV
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

//   Get relativistic velocity (beta)

        real get_velocity(real kinetic_energy) {

	      real gamma;
	      real beta;

      	      gamma <-1. +  kinetic_energy/m_electron();
	      beta <- sqrt(square(gamma)-1.)/gamma;
	      return beta;

	}

//  Beta decay function given an endpoint Q, and neutrino mass m, and a kinetic energy KE (valid only near the tail)

        real get_beta_function_log(real KE, real Q, real m_nu, real minKE) {

	     real log_rate;
	     real log_norm;
	     
	     log_norm <- 1.5 * log(square(Q - minKE) - square(m_nu));	     
	     log_rate <- log(3.) + log(Q - KE) + 0.5 * log(square(KE - Q) - square(m_nu));		

	     return (log_rate-log_norm);
	}


//  Total cross-section (in 1/(meters)^2)
//  Based on the paper Binary-encounter-dipole model for electron-impact ionization
//  Yong-Ki Kim and M. Eugene Rudd, Phys. Rev. A 50, 3954

        real xsection(real kinetic_energy, real ave_kinetic, real bind_energy, real msq, real Q) {
	     real beta;
	     real d_inf;
	     real S;
	     real xsec;
	     real t_energy;
	     real u_energy;
	     real b_energy;

	     beta <- get_velocity(kinetic_energy);
	     b_energy <- bind_energy;
	     t_energy <- (0.5 * m_electron() * beta * beta) / b_energy;
	     u_energy <- ave_kinetic / b_energy;

	     S <- 4.0 * pi() * square(bohr_radius()) / (t_energy + u_energy + 1) * square(ry_hydrogen()/b_energy);
	     d_inf <- b_energy * msq / ry_hydrogen();
	     xsec <- S * (d_inf * log(t_energy) + (2 - Q) * (1.0 - 1.0/t_energy - log(t_energy)/(1.0+t_energy)));
	     
	     return xsec;
	}

//  Butterworth-type filter.

       real filter_log(real s, real s_min, real s_max, real n) {
	     return -1./2. * ( log1p(pow(s_min/s,2.*n)) +log1p(pow(s/s_max,2.*n)) );
       }

       real signal_to_noise_log(real KE, real Q, real m_nu, real minKE, real maxKE, real signal_fraction) {

       	   real background_log;
	   real signal_log;
	   real rate_log;

    	   background_log <- log(1.-signal_fraction) - log(maxKE - minKE);

	   if (KE < (Q-fabs(m_nu))) {
       	      signal_log <- log(signal_fraction) + get_beta_function_log(KE, Q, m_nu, minKE);
       	      rate_log <- log_sum_exp(signal_log,  background_log);
    	   } else {
       	      rate_log <- background_log;
    	   }
	   return rate_log;  
	}
}

data {

//   Number of neutrinos and mixing parameters

     real neutrino_mass_limit;

//   Primary magnetic field (in Tesla)

     real<lower=0> BField;
     real BFieldError;

//   Range for fits (in Hz)

     real<lower=0 > minKE;
     real<lower=minKE> maxKE;

//   Endpoint of tritium, in eV

     real QValue;
     real QValue_Error;
     real sigmaQ;

//  Conditions of the experiment and measurement

     real number_density;				//  Tritium number density (in meter^-3)
     real temperature;				//  Temperature of gas (in Kelvin)
     real effective_volume;		        //  Effective volume (in meter^3)
     real measuring_time;			//  Measuring time (in seconds)

//  Clock and filter information

     real fBandpass;
     real fclockError;
     int  fFilterN;

//  Input data from generated sample

     int nData;
     vector[nData] time_data;
     vector[nData] freq_data;
     vector[nData] rate_data;
     int events[nData];

}

transformed data {

    real minFreq;
    real maxFreq;
    real fclock;
    real activity;

    minFreq <- get_frequency(maxKE, BField);
    maxFreq <- get_frequency(minKE, BField);

    fclock <- minFreq;

    if (fBandpass > (maxFreq-minFreq)) {
       print("Bandpass filter (",fBandpass,") is greater than energy range (",maxFreq-minFreq,").");
       print("Consider enlarging energy region.");
    }

    activity <- tritium_rate_per_eV() * pow(QValue - minKE,3) * number_density * effective_volume / (tritium_halflife() / log(2.) );
    print("total activity = ",activity * measuring_time, " events over ",measuring_time," seconds.")

}

parameters {

    real<lower=0.,upper=1.> signal_fraction;
    real<lower=0> scatt_width;
    real<lower=0> mu_tot;

    real uB;
    real uQ0;
    real uQ;
    real<lower=0.0> eDop;
    real<lower=-pi()/2.,upper=+pi()/2> uf;
    real<lower=-neutrino_mass_limit, upper=neutrino_mass_limit> neutrino_mass;
}

transformed parameters{

    real KE;
    real frequency;
    vector[nData] freq_recon;
    vector[nData] rate;
    real df;
    real signal_rate;
    real<lower=0> MainField;
    real Q0;
    real Q;
    real beta;
    real sum_log_rate;

    real rad_width;
    real tot_width;
    real sigma_freq;
    
    real kDoppler;
    real KE_shift;

    real signal_log;
    real background_log;
    real rate_log;
    real total_rate;
    
//   Obtain magnetic field (with prior distribution)

    MainField <- vnormal_lp(uB, BField, BFieldError);

//   Calculate scattering length, radiation width, and total width;

    rad_width <- cyclotron_rad(MainField);
    tot_width <- (scatt_width + rad_width);
    sigma_freq <- (scatt_width + rad_width) / (4. * pi());    

// Determine total rate from activity

    total_rate <- mu_tot * activity * measuring_time;
    sum_log_rate <- 0.;

// Dispersion due to uncertainty in final states (with prior distribution)

#  Determining endpoint

    Q0 <- vnormal_lp(uQ0, QValue, QValue_Error);

    Q  <- vnormal_lp(uQ, Q0, sigmaQ);
    
    df <- vcauchy_lp(uf, 0., sigma_freq);    

    for (i in 1:nData){

    	freq_recon[i] <- freq_data[i];
	
    	frequency <- freq_data[i] - df + fclock;

	KE <- get_kinetic_energy(frequency, BField);

	if ((KE > minKE) && (KE < maxKE)) {

	   beta <- get_velocity(KE);
     
    	   kDoppler <-  m_electron() * get_velocity(QValue) * sqrt(eDop / tritium_molecular_mass());

    	   KE_shift <- KE;

//   Determine signal and background rates from beta function and background level
    
    	   rate_log <- signal_to_noise_log(KE_shift, Q, neutrino_mass, minKE, maxKE, signal_fraction);
	   rate[i] <- total_rate * exp(rate_log);
	   sum_log_rate <- sum_log_rate + poisson_log(events[i], rate[i]);
	}
     }
}

model {

#  Thermal Doppler broadening of the tritium source

    eDop ~ gamma(1.5,1./(k_boltzmann() * temperature));

#  In-situ measurement of the collisional broadening term

    time_data ~ exponential(scatt_width);

#  Effect of filter in cleaning data

    for (i in 1:nData) {
    	freq_recon[i] ~ filter(0.0, fBandpass, fFilterN);
    }

#  The Poisson distribution of the beta decay and background

    increment_log_prob(sum_log_rate);    

}


