/*
* MC Krypton Model (Frequency Analysis Model)
* -----------------------------------------------------
* Author: J. A. Formaggio <josephf@mit.edu>
*
* Date: 23 July 2014
*
* Purpose: 
*
*		Program will analyze a set of sampled data from krypton runs
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

//   Primary magnetic field (in Tesla)

     	real<lower=0> BField;
	real<lower=0> BFieldError;

//   Secondary trapping magnetic field (in Tesla/milliAmp).  Error in Tesla.  Current in milliAmperes. 

     	real BCoil;
	real BCoilError;
  	real TrapCurrent;

//   Local oscillator and main mixer offset and error (in Hz)

   	real fclock;
  	real fclockError;
	real LOFreq;

//   Range for fits (in Hz)

  	real<lower=0 > minFreq;
  	real<lower=minFreq> maxFreq;

//   Broadening due to measurement

  	real frequencyWidth;

//   Kr Lines

     	int nLevels;
        real eGamma;
     	vector<lower=0.0>[nLevels] eParentLevel;
	vector<lower=0.0>[nLevels] eParentWidth;
     	vector<lower=0.0>[nLevels] eProgenyLevel;

//   Observed data (frequency and frequency loss).  Measured in Hz and Hz/s.

	int <lower=0> nData;
	vector[nData] freq_data;

}   

transformed data {
	    
	real minKE;
	real maxKE;

	real ePrimary;
	real eShakeoff;
	real eShakeup;

	int nLines;
	vector[nLevels*(nLevels+1)/2] eLineEnergy;
	vector[nLevels*(nLevels+1)/2] eLineWidth;

	minKE <- get_kinetic_energy(maxFreq, BField + BCoil * TrapCurrent);
	maxKE <- get_kinetic_energy(minFreq, BField + BCoil * TrapCurrent);

	nLines <- 0;
	for (i in 1:nLevels){

	    ePrimary <- eGamma - eParentLevel[i];
	    if ((ePrimary > minKE) && (ePrimary < maxKE)) {
	       nLines <- nLines+1;
	       eLineEnergy[nLines] <- ePrimary;
	       eLineWidth[nLines] <-  eParentWidth[i];
	    }

	    eShakeoff <- eGamma - eParentLevel[i] - eProgenyLevel[i];
	    if ((eShakeoff > minKE) && (eShakeoff < maxKE)) {
	       nLines <- nLines+1;
	       eLineEnergy[nLines] <- eShakeoff;
	       eLineWidth[nLines] <-  eParentWidth[i];
	    }

//	    Shakeup contribution; turn off for now.
	  if (1==0) {
	    for (j in 1:nLevels-i){
	    	eShakeup <- ePrimary - eParentLevel[i+j];
		if ((eShakeup > minKE) && (eShakeup < maxKE)) {
	           nLines <- nLines+1;
	       	   eLineEnergy[nLines] <- eShakeup;
	       	   eLineWidth[nLines] <-  eParentWidth[i] + eParentWidth[i+j];
	    	}
	    }
	  }
	}	    

	for (k in 1:nLines) {
	    print("Lines included :", k, " ->", eLineEnergy[k], " : ",eLineWidth[k]);
	}

}

parameters {

	vector[2] uNormal;
	real<lower=-pi()/2,upper=+pi()/2> uCauchy;
	vector<lower=-pi()/2,upper=+pi()/2>[nLines] zCauchy;

	real<lower=0.0> GlobalWidth;
	simplex[nLines] SourceStrength;

}

transformed parameters {

	real TrappingField;
	real MainField;
	real TotalField;

	real freq_shift;
	real dfWidth;
	real df;

	vector[nLines] theLines;

	vector[nData] frequency; 
	vector[nData] kinetic_energy; 

// Calculate primary magnetic field, trapping coil effect and total (minimum) field

	MainField <-  vnormal_lp(uNormal[1], BField, BFieldError);

	TrappingField <-  vnormal_lp(uNormal[2], BCoil, BCoilError) * TrapCurrent;

	TotalField <- MainField + TrappingField;

//  Calculate the smear of the frequency due to windowing and clock error (plus clock shift).  Assume cauchy distribution.

        freq_shift <- fclock + LOFreq;

	dfWidth <- sqrt(square(fclockError) + square(frequencyWidth));

	df <- vcauchy_lp(uCauchy, freq_shift, dfWidth);

//  Calculate lines

	for (k in 1:nLines) {
	    theLines[k] <- vcauchy_lp(zCauchy[k], eLineEnergy[k], eLineWidth[k]);
	}
	
//  Calculate observables from data

	frequency <- freq_data + df;

	for (n in 1:nData) {
	    kinetic_energy[n] <- get_kinetic_energy(frequency[n], TotalField);
	}

}

model{

	vector[nLines] ps;

//   Loop over events

     	for (n in 1:nData) {

//   Allow the kinetic energy to have a cauchy prior drawn from a parent global distribution
     	   for (k in 1:nLines) {
	       ps[k] <- log(SourceStrength[k]) + cauchy_log(kinetic_energy[n], theLines[k], GlobalWidth);
	    }		   
//  Increment likelihood based on amplitudes
	   increment_log_prob(+log_sum_exp(ps));	
	}

}

generated quantities{
	 
	  real freq_gen;
	  real energy_gen;
	  real prob_sum;
	  real peak_sum;

	  prob_sum <- 0.;
	  peak_sum <- uniform_rng(0.,1.);
	  for (k in 1:nLines) {
	      prob_sum <- prob_sum + SourceStrength[k];
	      if (peak_sum < prob_sum){              
	         peak_sum <- 2.0;
	      	 energy_gen <- cauchy_rng(eLineEnergy[k],GlobalWidth);
	      	 freq_gen <- get_frequency(energy_gen, TotalField);
	      }
	  }
}
