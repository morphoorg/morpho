/*
* MC Krypton Model (Generator)
* -----------------------------------------------------
* Author: J. A. Formaggio <josephf@mit.edu>
*
* Date: 23 July 2014
*
* Purpose: 
*
*		Program will generate a set of sampled data distributed according to the decay of 83mKr .
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
	real r0_electron() { return square(alpha())*bohr_radius();}  // Electron radius

// Method for converting kinetic energy (eV) to frequency (Hz).  
// Depends on stheta = sin(pitch angle) and magnetic field (Tesla)

   	real get_frequency(real kinetic_energy, real stheta, real field) {
	     real gamma;
	     gamma <- 1. +  kinetic_energy/m_electron();
	     return freq_c() / gamma * field * (1. + 1./square(stheta)) / 2.;
	}

// Method for converting frequency (Hz) to kinetic energy (eV)
// Depends on stheta = sin(pitch angle) and magnetic field (Tesla)

   	real get_kinetic_energy(real frequency, real stheta, real field) {
	     real gamma;
	     gamma <- freq_c() / frequency * field * 2./  (1. + 1./square(stheta));
	     return (gamma -1.) * m_electron();
	}

//  Get magnetic field (Tesla) correction due to harmonic potential averaging

        real get_magnetic_field(real field, real stheta) {
	     return field / 2. * (1. + 1./square(stheta));
	}

//   Get ideal radiated power (in eV/s)
//   Depends on kinetic energy (eV), stheta = sin(pitch angle) and magnetic field (Tesla)

        real get_power(real kinetic_energy, real stheta, real field) {

	      real gamma;
	      real beta;

      	      gamma <-1. +  kinetic_energy/m_electron();
	      beta <- sqrt(square(gamma)-1.)/gamma;
	      return (2./3.) * (m_electron() * r0_electron() /c()) * square(omega_c() * field)  * square(gamma * beta * stheta);

	}

//   Get loss in frequency over time (Hz/s)
//   Depends on kinetic energy (eV), stheta = sin(pitch angle) and magnetic field (Tesla)
     
        real get_frequency_loss(real kinetic_energy, real stheta, real field) {

	      real gamma;
	      real beta;
	      real PowerUnit;

	      gamma <-1. +  kinetic_energy/m_electron();
	      beta <- sqrt(square(gamma)-1.)/gamma;
	      PowerUnit <- get_power(kinetic_energy, stheta, field) ;

	      return 1/(2.*pi()) * (omega_c() * field) * PowerUnit / (2. * m_electron() * square(gamma)) * (1. + 1./square(stheta));

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

//   Number of signal and background models

	int<lower=0> nSignals;
     	int<lower=0> nBackgrounds;

//   Primary magnetic field (in Tesla)

     	real<lower=0> BField;
	real<lower=0> BFieldError;
  	real<lower=0> BFieldResolution;

//   Secondary trapping magnetic field (in Tesla/Amp).  Error in Tesla.  Current in Amperes. 

     	real BCoil;
	real BCoilError;
  	real BCoilCurrent;

//   Local oscillator offset and error (in Hz)

   	real fclock;
  	real fclockError;

//   Range for fits (in Hz)

  	real<lower=0 > minFreq;
  	real<lower=minFreq> maxFreq;

//   Allows one to alter the energy loss relationship by a constant offset

	real gCoupling;
	real gCouplingWidth;

//   Simulation-specific information on krypton lines

	vector[nSignals] FunctionAmplitude;
	vector[nSignals] FunctionAmplitudeError;
  	vector[nSignals] FunctionMean;
  	vector[nSignals] FunctionMeanError;
	vector[nSignals] FunctionWidth;

//   Broadening due to measurement

       real frequencyWidth;
       real dfdtWidth;

//   Signal and noise levels

  	real<lower=0.> SignalLevel;
	real<lower=0.> NoiseLevel;

}   

transformed data {
	    
        real minKE;
	real maxKE;

	minKE <- get_kinetic_energy(maxFreq, 1.0, BField);
	maxKE <- get_kinetic_energy(minFreq, 1.0, BField);

}

parameters {

	vector[3] uNormal;
	vector[nSignals] zNormal;
	real<lower=0., upper=1.> eUniform;
	real<lower=0., upper=1.> sUniform;

	real<lower=-pi()/2,upper=+pi()/2> uCauchy;

	simplex[nSignals] BranchRatio;
	real gPower;
}

transformed parameters {

	real<lower=0.,upper=1.> sthetamin;
	real MainField;
	real TrappingField;
	real TotalField;
	real df;
	real muB; 

	real stheta;
	real KE;

	vector[nSignals] BranchMean;

// Calculate primary magnetic field

	muB <-  vnormal_lp(uNormal[1], BField, BFieldError);
	MainField <- vnormal_lp(uNormal[2], muB, BFieldResolution);

// Calculate trapping coil effect and total (minimum) field

   	TrappingField  <- vnormal_lp(uNormal[3], BCoil* BCoilCurrent, BCoilError);
	TotalField <- MainField + TrappingField;

//  Calculate maximum pitch angle from trapping coil
    
        sthetamin <- sqrt(TotalField/MainField);

//  Calculate the smear of the frequency due to windowing and clock error (plus clock shift).  Assume normal distribution.

	df <- vcauchy_lp(uCauchy, fclock, fclockError);

// Calculate mean energy of each branch

	for (i in 1:nSignals) {
	    BranchMean[i] <- vnormal_lp(zNormal[i], FunctionMean[i], FunctionMeanError[i]);   
	}

//   Calculate sin(pitch angle) and kinetic energy assuming flat distributions

	stheta <- sthetamin + (1.-sthetamin)*sUniform;
	KE <- minKE + (maxKE - minKE) * eUniform;

}

model{

	real log_normalization;
	vector[nSignals+nBackgrounds] ps;

//   Calculate the power normalization factor

       gPower ~ normal(gCoupling, gCouplingWidth);

//  Distribute fraction of signal krypton events.  

	BranchRatio ~ normal(FunctionAmplitude/sum(FunctionAmplitude), FunctionAmplitudeError/sum(FunctionAmplitude));

//   Add in krypton lines

	for (k in 1:nSignals) {
	    ps[k] <-  log(SignalLevel) + log(BranchRatio[k]) + cauchy_log(KE,BranchMean[k],FunctionWidth[k]);
	}

//   Add in linear background in kinetic energy (i.e. background electrons)

        for (k in nSignals+1:nSignals+nBackgrounds) {
	    ps[k] <- log(NoiseLevel)  - log(maxKE-minKE);
	}

//  Increment likelihood based on amplitudes

	increment_log_prob(log_sum_exp(ps));	

}

generated quantities {

	real frequency; 
	real power;
	real dfdt;

	real freq_data;
	real dfdt_data;

//   Convert to observables for all data points.  Create for each data point.
	
	frequency <- get_frequency(KE, stheta, TotalField) - df;
	power <- gPower * get_power(KE, stheta, TotalField);
	dfdt <- gPower * get_frequency_loss(KE, stheta, TotalField);
	
	freq_data <- normal_rng(frequency, frequencyWidth);
	dfdt_data <- normal_rng(dfdt, dfdtWidth);

}
