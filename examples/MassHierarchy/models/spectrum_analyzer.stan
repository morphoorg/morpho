/*
* MC Neutrino Mass and Beta Decay Model - Analyzer
* -----------------------------------------------------
* Authors: Talia Weiss <tweiss@mit.edu>
*          J. A. Formaggio <josephf@mit.edu>
*
* Date: 9 July 2015
*
* Purpose:
*
* Constructs neutrino mass model in Stan with beta decay spectrum data generated using assumption of either normal or inverted mass hierarchy.
*
*/


functions{

    // Load libraries

    include_functions<-func_routines
    include_functions<-neutrino_mass_functions
    include_functions<-tritium_functions

}

data{

    real minKE;                 // Bounds on possible beta-decay spectrum kinetic energies in eV
    real maxKE;
    real Q;                     // Endpoint of beta-decay spectrum in eV - should be between minKE and maxKE
    real signal_fraction;       // Fraction of events that can be described as signal (as opposed to background)

    int nBinSpectrum;           // Number of spectral bins
    vector[nBinSpectrum] KE_data;        // Kinetic energies (eV) corresponding to rates from spectrum
    int n_spectrum_data[nBinSpctrum];    // List of number of events in each bin
}

parameters{

    vector<lower=0.0, upper=0.5>[3] nu_mass;    // Vector of neutrino masses (m1, m2, m3)
    real<lower=0.0>  sin2_th12;                      // Theta values generated from measured thetas and errors (above)
    real<lower=0.0>  sin2_th13;
}

transformed parameters {

    real delta_m21;
    real<lower=0.0>   delta_m32;        // Defined to always be positive
    real m32_withsign;      // Can be either positive or negative; sign indicates prefered hierarchy

    real<lower=0.0>  min_mass;  // Lowest mass, determined by minimizing nu_mass, in eV
    vector<lower=0.0>[3] Ue_squared;   // Squares of PMNS matrix elements U_e, calculated using mixing angles distributions
    real<lower=0.0>  mbeta;     // "Total" neutrino mass measurement in eV

    vector[nBinSpectrum] rate_log;    // Beta decay spectrum points fit using inputted (KE, N) points

    delta_m21 <- square(nu_mass[2]) - square(nu_mass[1]);
    delta_m32 <- sqrt(square(square(nu_mass[3]) - square(nu_mass[2])));
    m32_withsign <- square(nu_mass[3]) - square(nu_mass[2]);

    min_mass <- min(nu_mass);
    Ue_squared <- get_U_PMNS(nFamily, sin2_th12, sin2_th13);
    mbeta <- get_effective_mass(Ue_squared, nu_mass);

    for(j in 1:nBinSpectrum) {
        rate_log[j] <- signal_to_noise_log(KE_data[j], Q, Ue_squared, nu_mass, minKE, maxKE, signal_fraction);
}
}

model {

// Create distribution for each parameter (below)

    if (m32_withsign > 0.){
        delta_m32 ~ normal(meas_delta_m32_NH, meas_delta_m32_NH_err);
        sin2_th13 ~ normal(meas_sin2_th13_NH, meas_sin2_th13_NH_err);
    }
    
    else{
        delta_m32 ~ normal(meas_delta_m32_IH, meas_delta_m32_IH_err);
        sin2_th13 ~ normal(meas_sin2_th13_IH, meas_sin2_th13_IH_err);
    }
    
    th12 ~ normal(sin_sq_2meas_th12, sin_sq_2meas_th12_err);
    delta_m21 ~ normal(meas_delta_m21, meas_delta_m21_err);

// Fit beta decay spectrum to poisson distribution of inputted generated data points

for (i in 1:nBinSpectrum)
  {
    if(n_spectrum_data[i]>0 )
    {
      increment_log_prob(poisson_log(n_spectrum_data[i],rate_log[i])); //May require rate_log[i]*widthBin[i], instead
    }
    if (rate_log[i]<0)
    {
      print(rate_log[i],i);
    }
  }

}
