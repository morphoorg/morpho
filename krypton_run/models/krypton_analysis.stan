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

   	vector get_kinetic_energy(vector frequency, real stheta, real field) {
	     return ((freq_c() * field * 2./  (1. + 1./square(stheta))) ./ frequency -1.) * m_electron();
	}

   	real get_kinetic_energy(real frequency, real stheta, real field) {
	     return ((freq_c() * field * 2./  (1. + 1./square(stheta))) / frequency -1.) * m_electron();
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

//   Run-specific settings

	real LOFreq;
  	real TrapCurrent;
	real LivetimeWeight;

//   Observed data and errors.  Measured in Hz and Hz/s.

	int <lower=0> nData;
	vector[nData] freq_data;
	vector[nData] dfdt_data;

}   

transformed data {
	    
        real minKE;
	real maxKE;
	real RunLivetime;
	real freq_shift;

	minKE <- get_kinetic_energy(maxFreq, 1.0, BField);
	maxKE <- get_kinetic_energy(minFreq, 1.0, BField);
	RunLivetime <- 1.0 ./ LivetimeWeight;

	 freq_shift <- fclock + LOFreq * 1.e6;

}

parameters {

	vector[3] uNormal;
	real<lower=0., upper=1.> eUniform;
	real<lower=0., upper=1.> sUniform;

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
	real<lower=0., upper=2.0> muB; 
	real df;
	real dfWidth;

	real TotalField;
	real sthetamin;
	real stheta;

//  Calculate the smear of the frequency due to windowing and clock error (plus clock shift).  Assume normal distribution.

	dfWidth <- sqrt(square(fclockError) + square(frequencyWidth));
	df <- vcauchy_lp(uCauchy, freq_shift, dfWidth);

// Calculate primary magnetic field

	muB <-  vnormal_lp(uNormal[1], BField, BFieldError);
	MainField <- vnormal_lp(uNormal[2], muB, BFieldResolution);

// Calculate trapping coil effect and total (minimum) field
	    
      	TrappingField  <- vnormal_lp(uNormal[3], BCoil, BCoilError);
	TotalField <- MainField + TrappingField * (TrapCurrent / 1000.) ;

//  Calculate maximum pitch angle from trapping coil

	sthetamin <- sqrt(TotalField / MainField);

//   Calculate sin(pitch angle) and kinetic energy assuming flat distributions

	stheta <- sthetamin + (1.-sthetamin)*sUniform;

}

model{

        real lambda_sum;
	vector[nSignals+nBackgrounds] ps;
        real Signal;
	real Background;

	vector[nData] KE;
	vector[nData] frequency; 
	vector[nData] dfdt;
	vector[nData] power;
	
//   Calculate the power normalization factor

        gPower ~ normal(gCoupling, gCouplingWidth);

	if (usePower > 0) dfdt_data ~ normal(dfdt, dfdtWidth);

        lambda_sum <- 0.;

//  Calculate observables from data

	frequency <- freq_data + df;
	KE <-get_kinetic_energy(frequency, stheta, TotalField);

	for (n in 1:nData) {

//  Calculate observables from data

	    power[n] <- gPower * get_power(KE[n], stheta, TotalField);
	    dfdt[n] <- gPower * get_frequency_loss(KE[n], stheta, TotalField);

//   Allow the kinetic energy to have a cauchy prior drawn from a parent global distribution

	    if (TrapCurrent > 0) {
		   for (k in 1:nSignals) {
 	       	       ps[k] <-  log(SignalRate * RunLivetime) + log(SourceStrength[k]) + cauchy_log(KE[n],SourceMean[k],SourceWidth[k]);
	       	       lambda_sum <- lambda_sum + SignalRate * RunLivetime * SourceStrength[k] * (cauchy_cdf(maxKE,SourceMean[k],SourceWidth[k]) - cauchy_cdf(minKE,SourceMean[k],SourceWidth[k]));
	   	   }
	    }
        	for (k in nSignals+1:nSignals+nBackgrounds) {
	       	    ps[k] <- log(BackgroundRate * RunLivetime) - log(maxKE - minKE);
	       	    lambda_sum <- lambda_sum + BackgroundRate * RunLivetime;
            }

//  Increment likelihood based on amplitudes

	      increment_log_prob(+log_sum_exp(ps));	
	      increment_log_prob(-log(lambda_sum));	
	}

//  Include extended likelihood into fit

	Signal <- SignalRate * RunLivetime;
	Background <- BackgroundRate * RunLivetime;

	nData ~ poisson(Signal + Background);

}

generated quantities {

	vector[nSignals] freq_rec;

//   Convert to observables for all data points.  Create for each data point.
	
	for (n in 1:nSignals)
	    freq_rec[n] <- get_frequency(SourceMean[n], stheta, TotalField) - df;
}
