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
    include_functions<-MH_Functions

}

data{

    // Neutrino mixing parameters
    real  meas_delta_m21;       // Best known value of delta_m2^2-delta_m1^2 in eV^2
    real  meas_delta_m21_err;   // Error on delta_m2^2-delta_m1^2 in eV^2
    real  meas_delta_m32;       // Best known value of delta_m3^2-delta_m2^2 in eV^2
    real  meas_delta_m32_err;   // Error on delta_m3^2-delta_m2^2 in eV^2
    real  sin_sq_2meas_th12;    // Best known value of sin squared of 2*theta_12 (radians)
    real  sin_sq_2meas_th12_err;// Error on sin squared of 2*theta_12
    real  sin_sq_2meas_th13;    // Best known value of sin squared of 2*theta_13
    real  sin_sq_2meas_th13_err;// Error on sin squared of 2*theta_13

    real minKE;                 // Bounds on possible beta-decay spectrum kinetic energies in eV
    real maxKE;
    real Q;                     // Endpoint of beta-decay spectrum in eV - should be between minKE and maxKE
    real signal_fraction;       // Fraction of events that can be described as signal (as opposed to background)

    //int numPts;                 // Number of data points generated previously
    //real norm;                  // Temporary normalization for Poisson distribution of spectrum

    int nBinSpectrum;           // Number of spectral bins
    vector[nBinSpectrum] KE_data;        // Kinetic energies (eV) corresponding to rates from spectrum
    int n_spectrum_data[nBinSpctrum];    // List of number of events in each bin
}

parameters{

    vector<lower=0.0, upper=0.5>[3] nu_mass;    // Vector of neutrino masses (m1, m2, m3)
    real<lower=0.0>  th12;                      // Theta values generated from measured thetas and errors (above)
    real<lower=0.0>  th13;
}

transformed parameters {

    real delta_m21;
    real<lower=0.0>   delta_m32;        // Defined to always be positive
    real m32_withsign;      // Can be either positive or negative; sign indicates prefered hierarchy

    real<lower=0.0>  min_mass;  // Lowest mass, determined by minimizing nu_mass, in eV
    vector<lower=0.0>[3] sUe;   // Squares of PMNS matrix elements U_e, calculated using mixing angles distributions
    real<lower=0.0>  mbeta;     // "Total" neutrino mass measurement in eV

    vector[nBinSpectrum] rate_log;    // Beta decay spectrum points fit using inputted (KE, N) points

    delta_m21 <- square(nu_mass[2]) - square(nu_mass[1]);
    delta_m32 <- sqrt(square(square(nu_mass[3]) - square(nu_mass[2])));
    m32_withsign <- square(nu_mass[3]) - square(nu_mass[2]);

    min_mass <- min(nu_mass);
    sUe <- matrix_elements(th12, th13);
    mbeta <- sqrt(square(nu_mass[1])*sUe[1] + square(nu_mass[2])*sUe[2] + square(nu_mass[3])*sUe[3]);

    for(j in 1:nBinSpectrum) {
        rate_log[j] <- signal_to_noise_log(KE_data[j], Q, sUe, nu_mass, minKE, maxKE, signal_fraction);
}
}

model {

// Create distribution for each parameter (below)

    th12 ~ normal(sin_sq_2meas_th12, sin_sq_2meas_th12_err);
    th13 ~ normal(sin_sq_2meas_th13, sin_sq_2meas_th13_err);
    delta_m21 ~ normal(meas_delta_m21, meas_delta_m21_err);
    delta_m32 ~ normal(meas_delta_m32, meas_delta_m32_err);

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
