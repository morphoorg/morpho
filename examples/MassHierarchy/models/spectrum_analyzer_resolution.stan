/*
* MC Neutrino Mass and Beta Decay Model - Spectrum Analyzer
* ------------------------------------------------------------
* Authors: Talia Weiss <tweiss@mit.edu>
*          J. A. Formaggio <josephf@mit.edu>
           M. Guigue <mathieu.guigue@pnnl.gov>
*
* Date: 1 November 2016
*
* Purpose:
*
* Fit a measured spectrum including an energy resolution.
* The fitted spectrum is a 2-kinks model, but it should be easy to adapt it to more than 2-kinks.
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

    int nBinSpectrum;           	// Number of spectral bins
    vector[nBinSpectrum] KE_data;       // Kinetic energies (eV) corresponding to rates from spectrum
    int n_spectrum_data[nBinSpectrum];  // List of number of events in each bin
    real measuring_time; //Duration of acquisition

}

parameters{

    real<lower=0.> amplitude;
    real uQ;
    vector<lower=0., upper=0.4>[2] nu_mass;    // Vector of neutrino masses (m,  m3)

    simplex[2] U_squared; //two kinks neutrinos
    real<lower=0., upper=2.> resolution;
    real<lower=0.,upper=0.000001> background_rate;

}

transformed parameters {

    real Q;
    real spectrum_shape;
    real spectrum;
    real widthBin;
    vector[nBinSpectrum] n_spectrum_recon;

    widthBin = (maxKE - minKE)/nBinSpectrum;

    // Incrementing log probability to incorporate endpoint distribution
    // Q = vnormal_lp(uQ, Q_mean, Q_err);
    Q = uQ; //no prior

    // Determine predicted spectral shape from kinetic energy data
    // simplex[3] Ue_squared;
    // Ue_squared[1] = U_squared[1]; // Ue1 = U
    // Ue_squared[2] = 0 ; // Ue2 = 0
    // Ue_squared[3] = U_squared[2]; // Ue3 = 1-U
    //
    // vector<lower=0., upper=0.4>[3] nu_mass;
    // nu_mass[1] = mass[1]; // m1 approx m
    // nu_mass[2] = mass[1]; // m2 approx m (could have set it to zero too)
    // nu_mass[3] = mass[2]; //m3 = m3



    for(j in 1:nBinSpectrum) {
        spectrum_shape = smeared_spectral_shape(KE_data[j], Q, U_squared, nu_mass,resolution);
	      spectrum = spectrum_shape * amplitude + background_rate * measuring_time;

	      n_spectrum_recon[j] = spectrum * widthBin;
    	  if (n_spectrum_recon[j]<0.){
      	     print(n_spectrum_recon[j],"  ", spectrum,"  ", widthBin,"   ", spectrum_shape);
  	    }
	 }

}


model {

// Fit beta decay spectrum to poisson distribution of inputted generated data points

    n_spectrum_data ~ poisson(n_spectrum_recon);

}
