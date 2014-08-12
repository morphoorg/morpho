/*
* MC Krypton Model (Analysis Model)
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

//   Local oscillator offset and error (in Hz)

   	real fclock;
  	real fclockError;

//   Range for fits (in Hz)

  	real<lower=0 > minFreq;
  	real<lower=minFreq> maxFreq;

//   Allows one to alter the energy loss relationship by a constant offset

        int  usePower;
	real gCoupling;
	real gCouplingWidth;

  	real frequencyWidth;
  	real dfdtWidth;

//   Observed data and errors.  Measured in Hz and Hz/s.

	int <lower=0> nData;
	vector[nData] freq_data;
	vector[nData] dfdt_data;
  	vector[nData] TrapCurrent;
	vector[nData] LivetimeWeight;

}   

transformed data {
	    
        real minKE;
	real maxKE;
	vector[nData] RunLivetime;

	minKE <- get_kinetic_energy(maxFreq, 1.0, BField);
	maxKE <- get_kinetic_energy(minFreq, 1.0, BField);
	RunLivetime <- 1.0 ./ LivetimeWeight;

}

parameters {

	vector[3] uNormal;
	vector<lower=0., upper=1.>[nData] eUniform;
	vector<lower=0., upper=1.>[nData] sUniform;

	real<lower=-pi()/2,upper=+pi()/2> uCauchy;

	real gPower;

	vector<lower=minKE, upper=maxKE>[nSignals] SourceMean;
	vector<lower=0., upper = 1.e9>[nSignals] SourceWidth;
	simplex[nSignals] SourceStrength;

	real<lower=0.> SignalRate;
	real<lower=0.> BackgroundRate;
}

transformed parameters {

	real MainField;
	real TrappingField;
	real muB; 
	real df;

	vector[nData] TotalField;
	vector[nData] sthetamin;
	vector[nData] stheta;
	vector[nData] KE;

	vector[nData] frequency; 
	vector[nData] dfdt;
	vector[nData] power;
	

//  Calculate the smear of the frequency due to windowing and clock error (plus clock shift).  Assume normal distribution.

	df <- vcauchy_lp(uCauchy, fclock, fclockError);

// Calculate primary magnetic field

	muB <-  vnormal_lp(uNormal[1], BField, BFieldError);
	MainField <- vnormal_lp(uNormal[2], muB, BFieldResolution);
      	TrappingField  <- vnormal_lp(uNormal[3], BCoil, BCoilError);
	TotalField <- MainField + TrappingField * (TrapCurrent / 1000.) ;

// Calculate trapping coil effect and total (minimum) field
	    
	for (n in 1:nData) {

//  Calculate maximum pitch angle from trapping coil

	        sthetamin[n] <- sqrt(TotalField[n] / MainField);

//   Calculate sin(pitch angle) and kinetic energy assuming flat distributions

	        stheta[n] <- sthetamin[n] + (1.-sthetamin[n])*sUniform[n];
	        KE[n] <- minKE + (maxKE - minKE) * eUniform[n];

//   Convert to observables for all data points.  Create for each data point.
	
		frequency[n] <- get_frequency(KE[n], stheta[n], TotalField[n]) - df;
		power[n] <- gPower * get_power(KE[n], stheta[n], TotalField[n]);
		dfdt[n] <- gPower * get_frequency_loss(KE[n], stheta[n], TotalField[n]);
	}

}

model{

        real Signal;
	real Background;
	vector[nSignals+nBackgrounds] ps;

//   Allow the kinetic energy to have a cauchy prior drawn from a parent global distribution

	for (n in 1:nData) {
		if (TrapCurrent[n] > 0) {
	   	   for (k in 1:nSignals) {
	    	       ps[k] <-  log(SignalRate * RunLivetime[n]) + log(SourceStrength[k]) + cauchy_log(KE[n],SourceMean[k],SourceWidth[k]);
	    	   }
		}
        	for (k in nSignals+1:nSignals+nBackgrounds) {
	    	    ps[k] <- log(BackgroundRate * RunLivetime[n]) - log(maxKE - minKE);
		}
		increment_log_prob(+log_sum_exp(ps));
	}

//	Calculate signal and noise contributions to total rate

	Signal <- sum(SignalRate * (RunLivetime));
	Background <- sum(RunLivetime * BackgroundRate);

//	nData ~ poisson(Signal + Background);

//   Assume data is gaussian-distributed around the predicted frequency and power loss

	freq_data ~ normal(frequency, frequencyWidth);

//   Calculate the power normalization factor

        gPower ~ normal(gCoupling, gCouplingWidth);

	if (usePower > 0) dfdt_data ~ normal(dfdt, dfdtWidth);

}

