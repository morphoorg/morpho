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
	     gamma <- freq_c() / frequency * field * (1. + 1./square(stheta))/2.;
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

//   Secondary trapping magnetic field (in Tesla/milliAmp).  Error in Tesla.  Current in milliAmperes. 

     	real BCoil;
  	real TrapCurrent;
	real TrapCurrentError;

//   Radial gradient of magnetic field (in Tesla/mm^2/mA).  Radial distance in millimeters

        real BGradient;
	real maxRadius;     	       

//   Local oscillator and main mixer offset and error (in Hz)

   	real fclock;
  	real fclockError;
	real LOFreq;

//   Range for fits (in Hz)

  	real<lower=0 > minFreq;
  	real<lower=minFreq> maxFreq;

//   Allows one to alter the energy loss relationship by a constant offset

	real gCoupling;
	real gCouplingWidth;

//   Broadening due to measurement

  	real frequencyWidth;
  	real dfdtWidth;

//   Observed data (frequency and frequency loss).  Measured in Hz and Hz/s.

	int <lower=0> nData;
	vector[nData] freq_data;
	vector[nData] dfdt_data;

//   Livetime weighting

	vector[nData] LivetimeWeight;

//   Flag to determine if to use power loss in fit

        int  usePower;

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

	vector[2] uNormal;
	real<lower=0., upper=1.> sUniform;
	real<lower=0., upper=1.> rUniform;
	real<lower=-pi()/2,upper=+pi()/2> uCauchy;

	vector<lower=minKE, upper=maxKE>[nSignals] SourceMean;
	vector<lower=0., upper = 1.e9>[nSignals] SourceWidth;
	vector[nSignals] SourceSkew;
	simplex[nSignals] SourceStrength;

	real gPower;

	real<lower=0.> SignalRate;
	real<lower=0.> BackgroundRate;
}

transformed parameters {

	real ITrap;
	real TrappingField;
	real MainField;
	real BGradientField;
	real TotalField;

	real radius_sq;
	real sthetamin;

	real freq_shift;
	real dfWidth;
	real df;

// Calculate primary magnetic field

	MainField <-  vnormal_lp(uNormal[1], BField, BFieldError);

//  Calculate radius

	radius_sq <- rUniform * square(maxRadius);

// Calculate trapping coil current

   	ITrap <- vnormal_lp(uNormal[2], TrapCurrent, TrapCurrentError);	

// Calculate trapping coil effect and total (minimum) field

	TrappingField <- BCoil * ITrap;

	BGradientField <- BGradient * radius_sq * ITrap;

	TotalField <- MainField + TrappingField + BGradientField;

//  Calculate minimum angle allowed

        sthetamin <- sqrt(TotalField/(TotalField-TrappingField));

//  Calculate the smear of the frequency due to windowing and clock error (plus clock shift).  Assume cauchy distribution.

        freq_shift <- fclock + LOFreq;
	dfWidth <- sqrt(square(fclockError) + square(frequencyWidth));
	df <- vcauchy_lp(uCauchy, freq_shift, dfWidth);

}

model{

	vector[nSignals+nBackgrounds] ps;
        real Signal;
	real Background;

	real logdKdf;

	real lambda;

        real stheta;
	real KE;
	real dfdt;
	real power;
	
	vector[nData] frequency; 

//   Calculate the power normalization factor

        gPower ~ normal(gCoupling, gCouplingWidth);

	if (usePower > 0) dfdt_data ~ normal(dfdt, dfdtWidth);

//  Calculate observables from data

	frequency <- freq_data + df;

//  Calculate average number of expected events based on Poisson distribution

	lambda <- (SignalRate + BackgroundRate)*mean(RunLivetime);

//  Calculate pitch angle assuming flat distribution

	stheta <- sthetamin + (1.-sthetamin)*sUniform;

//   Loop over events

	for (n in 1:nData) {

	    KE <-get_kinetic_energy(frequency[n], stheta, TotalField);

//  Calculate observables from data

	    power <- gPower * get_power(KE, stheta, TotalField);
	    dfdt <- gPower * get_frequency_loss(KE, stheta, TotalField);

//   Allow the kinetic energy to have a cauchy prior drawn from a parent global distribution

            logdKdf <- log(KE + m_electron()) - log(get_frequency(KE, stheta, TotalField));

	    if (TrapCurrent > 0 && nSignals>0) {
		   for (k in 1:nSignals) {
 	       	       ps[k] <-  log(SignalRate * RunLivetime[n]) + log(SourceStrength[k]) + cauchy_log(KE,SourceMean[k],SourceWidth[k])+ logdKdf;
	   	   }		   
	    }

	    if (nBackgrounds>0) {
        	for (k in nSignals+1:nSignals+nBackgrounds) {
	       	    ps[k] <- log(BackgroundRate * RunLivetime[n]) - log(maxFreq - minFreq);
            	}
	    }

//  Increment likelihood based on amplitudes

	      increment_log_prob(+log_sum_exp(ps));	
	      increment_log_prob(-log(lambda));
	}

	nData ~ poisson(lambda);

}
