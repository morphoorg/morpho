/*
* MC Neutrino Mass and Beta Decay Model - Mass and Spectrum Analyzer
* ------------------------------------------------------------------
* Authors: Talia Weiss <tweiss@mit.edu>
*          J. A. Formaggio <josephf@mit.edu>
*
* Date: 1 Sept 2016
*
* Purpose:
*
* Constructs neutrino mass model in Stan with beta decay spectrum
* data generated using assumption of either normal or inverted mass
* hierarchy. Incorporates external mixing parameter information.
*
* To do: replace mixing parameter values with the ones in
* experiment_data.txt
*
*/


functions{

    // Load libraries

    include=constants;
    include=func_routines;
    include=neutrino_mass_functions;
    include=tritium_functions;

}

data{

    real minKE;				// Bounds on possible beta-decay spectrum kinetic energies in eV
    real maxKE;
    real Q_mean;				// Endpoint of beta-decay spectrum in eV - should be between minKE and maxKE
    real Q_err;
    real signal_fraction;       	// Fraction of events that can be described as signal (as opposed to background)

    int nBinSpectrum;           	// Number of spectral bins
    vector[nBinSpectrum] KE_data;       // Kinetic energies (eV) corresponding to rates from spectrum
    int n_spectrum_data[nBinSpectrum];  // List of number of events in each bin

    real activity;
    real measuring_time;		// In seconds
    real background_rate_mean; 		// In Hz/eV

}

parameters{

    vector<lower=0.0, upper=1.5>[3] nu_mass;    // Vector of neutrino masses (m1, m2, m3)
    real uQ;

    real<lower=0.0>  sin2_th12;                      // Theta values generated from measured thetas and errors
    real<lower=0.0>  sin2_th13;

    real<lower=minKE, upper=maxKE> KE_check;
}

transformed parameters {

    real delta_m21;
    real<lower=0.0>   delta_m32;        // Defined to always be positive
    real m32_withsign;      // Can be either positive or negative; sign indicates prefered hierarchy

    real<lower=0.0>  min_mass;  // Lowest mass, determined by minimizing nu_mass, in eV
    vector<lower=0.0>[3] Ue_squared;   // Squares of PMNS matrix elements U_e, calculated using mixing angles distributions
    real<lower=0.0>  mbeta;     // "Total" neutrino mass measurement in eV

    real<lower=minKE> Q;
    real spectrum_shape;
    real spectrum;
    real widthBin;
    vector[nBinSpectrum] n_spectrum_recon;
    
    real simple_rate_check;
    real spectrum_rate_check;

    delta_m21 = square(nu_mass[2]) - square(nu_mass[1]);
    delta_m32 = sqrt(square(square(nu_mass[3]) - square(nu_mass[2])));
    m32_withsign = square(nu_mass[3]) - square(nu_mass[2]);

    min_mass = min(nu_mass);
    Ue_squared = get_U_PMNS(nFamily(), sin2_th12, sin2_th13);
    mbeta = get_effective_mass(Ue_squared, nu_mass);

    widthBin = (maxKE - minKE)/nBinSpectrum;

    for(j in 1:nBinSpectrum) {
        spectrum_shape = spectral_shape(KE_data[j], Q, Ue_squared, nu_mass);
	spectrum = spectrum_shape * activity * measuring_time + background_rate_mean * measuring_time;

	 n_spectrum_recon[j] = spectrum * widthBin;
    	 if (n_spectrum_recon[j]<0.)
    	    {
      	     print(sin2_th12,"  ", sin2_th13);
      	     print(n_spectrum_recon[j],"  ", spectrum,"  ", widthBin,"   ", spectrum_shape);
  	    }
	 }

    simple_rate_check = spectral_shape(KE_check, Q, Ue_squared, nu_mass);
    spectrum_rate_check = measuring_time*(simple_rate_check*activity+background_rate_mean);

     Q = vnormal_lp(uQ, Q_mean, Q_err);

}


model {

// Create distribution for each parameter

    if (m32_withsign > 0.){
        meas_delta_m32_NH() ~ normal(m32_withsign, meas_delta_m32_NH_err());
        meas_sin2_th13_NH() ~ normal(sin2_th13, meas_sin2_th13_NH_err());
    }
    
    else{
        meas_delta_m32_IH() ~ normal(m32_withsign, meas_delta_m32_IH_err());
        meas_sin2_th13_IH() ~ normal(sin2_th13, meas_sin2_th13_IH_err());
    }
    
    meas_sin2_th12() ~ normal(sin2_th12, meas_sin2_th12_err());
    meas_delta_m21() ~ normal(delta_m21, meas_delta_m21_err());



// Fit beta decay spectrum to poisson distribution of inputted generated data points

    n_spectrum_data ~ poisson(n_spectrum_recon);



}
