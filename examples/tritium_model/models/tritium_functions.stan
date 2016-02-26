/*
* Tritium Spectrum Model (Analysis)
* -----------------------------------------------------
* Copyright: J. A. Formaggio <josephf@mit.edu>
*
* Date: 25 March 2015
* Modified: Feb 9 2016 by MG
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

	real tritium_rate_per_eV() {return 1.5e-13;}				 // fraction of rate in last 1 eV
	real tritium_molecular_mass() {return  2. * 3.016 * unit_mass();}   	 // Molecular tritium mass in eV
	real tritium_halflife() {return 12.32 * seconds_per_year();}  // Halflife of tritium (in seconds)

	// Method to fill the first line of the U_PMNS with the mean value of the sin(theta)

	vector get_U_PMNS(int nFamily, real sin2_th12, real sin2_th13) {
		vector[nFamily] U;
		U[1] <- (1. - sin2_th13) * (1. - sin2_th12);
		U[2] <- (1. - sin2_th13) * sin2_th12;
		U[3] <- sin2_th13 * sin2_th12;
		return U;
	}

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

	real beta_integral(real Q, real m_nu, real minKE) {
		return pow(square(Q - minKE) - square(m_nu),1.5);
	}

	real get_beta_function_log(real KE, real Q, real m_nu, real minKE) {

		real log_rate;
		real log_norm;

		log_norm <- log(beta_integral(Q, m_nu, minKE));
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

	// rate of events calculation

	real signal_to_noise_log(real KE, real Q, vector U, vector m_nu, real minKE, real maxKE, real signal_fraction) {

		int nFamily;           // Number of neutrino species
		real background_log;   // Log of background event rate --> log sum of background fraction and KE range
		real signal;            // Spectrum function above modified to incorporate [nFamily] masses
		real rate_log;         // Log of event rate (beta decay spectrum) --> log sum of signal and background
		real int_signal;     // Integral of the signal

		nFamily <- num_elements(U);

		background_log <- log(1.-signal_fraction) - log(maxKE - minKE);

		int_signal <- 0.; //initialize the integrated signal

		for (i in 1:nFamily){
			int_signal <- int_signal + U[i]*beta_integral(Q,m_nu[i],minKE); //recursive integration of the beta_spectrum for every neutrino mass
		}

		signal <- 0.;
		for (i in 1:nFamily){
			if (KE < (Q-fabs(m_nu[i]))) {
				signal <-signal + signal_fraction*U[i]*(Q-KE)*sqrt(square(KE-Q)-square(m_nu[i]))/int_signal;
			}
		}
		rate_log <- log(signal + exp(background_log)); //we add the background to the signal
		return rate_log;
	}
}
