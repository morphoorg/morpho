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

// Finds vector of squares of PMNS matrix elements U_e

    vector matrix_elements(real meas_th12, real meas_th13) {
        vector<lower=0.0>[3] sUe_fixed;

        sUe_fixed[1] <- square(cos(meas_th12)*cos(meas_th13));
        sUe_fixed[2] <- square(sin(meas_th12)*cos(meas_th13));
        sUe_fixed[3] <- square(sin(meas_th13));

        return sUe_fixed;
}

    real beta_integral(real Q, real m_nu, real minKE) {
        return pow(square(Q - minKE) - square(m_nu),1.5);
}

// Method for generating beta decay spectrum (log of event rate) given a single neutrino mass value

    real get_beta_function_log(real KE, real Q, real m_nu, real minKE) {

        real log_rate;
        real log_norm;
    
        log_norm <- log(beta_integral(Q, m_nu, minKE));
        log_rate <- log(3.) + log(Q - KE) + 0.5 * log(square(KE - Q) - square(m_nu));

        return (log_rate-log_norm);
}

// Method for generating beta decay spectrum with a flat background (larger signal fraction -> more background)
// Uses vector of neutrino masses of size nFamily (3)

    real signal_to_noise_log(real KE, real Q, vector U, vector m_nu, real minKE, real maxKE, real signal_fraction) {

        int nFamily;           // Number of neutrino species
        real background_log;   // Log of background event rate --> log sum of background fraction and KE range
        real signal_log;       // Spectrum function above modified to incorporate [nFamily] masses
        real rate_log;         // Log of event rate (beta decay spectrum) --> log sum of signal and background

        nFamily <- num_elements(U);

        background_log <- log(1.-signal_fraction) - log(maxKE - minKE);

        for (i in 1:nFamily){
            if (KE < (Q-fabs(m_nu[i]))) {
                signal_log <- log(signal_fraction) + log(U[i]) + get_beta_function_log(KE, Q, m_nu[i], minKE);
                rate_log <- log_sum_exp(signal_log,  background_log);
            }
            else {
                rate_log <- background_log;     // Once KE >= the endpoint, spectrum only consists of background
      	      }
      }
        return rate_log;
}
}


data{

    // Neutrino mixing parameters
    real meas_delta_m21;       // Best known value of delta_m2^2-delta_m1^2 in eV^2
    real  meas_delta_m21_err;   // Error on delta_m2^2-delta_m1^2 in eV^2
    real  meas_delta_m32;       // Best known value of delta_m3^2-delta_m2^2 in eV^2
    real  meas_delta_m32_err;   // Error on delta_m3^2-delta_m2^2 in eV^2
    real  meas_th12;            // Best known value of theta_12 (radians)
    real  meas_th12_err;        // Error on theta_12
    real  meas_th13;            // Best known value of theta_12
    real  meas_th13_err;        // Error on theta_13

    real minKE;                 // Bounds on possible beta-decay spectrum kinetic energies in eV
    real maxKE;
    real Q;                     // Endpoint of beta-decay spectrum in eV - should be between minKE and maxKE
    real signal_fraction;       // Fraction of events that can be described as signal (as opposed to background)

    int numPts;                 // Number of data points generated previously
    real norm;                  // Temporary normalization for Poisson distribution of spectrum

    int N[numPts];              // Log rates from generated beta decay spectrum
    vector[numPts] KEin;        // Kinetic energies (eV) corresponding to rates from spectrum
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
    vector<lower=0.0>[3] sUe;   // Squares of PMNS matrix elements U_e, calculated using mixing angle distributions
    real<lower=0.0>  mbeta;     // "Total" neutrino mass measurement in eV

    vector[numPts] rate_log;    // Beta decay spectrum points fit using inputted (KE, N) points

    delta_m21 <- square(nu_mass[2]) - square(nu_mass[1]);
    delta_m32 <- sqrt(square(square(nu_mass[3]) - square(nu_mass[2])));
    m32_withsign <- square(nu_mass[3]) - square(nu_mass[2]);

    min_mass <- min(nu_mass);
    sUe <- matrix_elements(th12, th13);
    mbeta <- sqrt(square(nu_mass[1])*sUe[1] + square(nu_mass[2])*sUe[2] + square(nu_mass[3])*sUe[3]);

    for(j in 1:numPts) {
        rate_log[j] <- signal_to_noise_log(KEin[j], Q, sUe, nu_mass, minKE, maxKE, signal_fraction);
}
}

model {

// Create distribution for each parameter (below)

    th12 ~ normal(meas_th12, meas_th12_err);
    th13 ~ normal(meas_th13, meas_th13_err);
    delta_m21 ~ normal(meas_delta_m21, meas_delta_m21_err);
    delta_m32 ~ normal(meas_delta_m32, meas_delta_m32_err);

// Fit beta decay spectrum to poisson distribution of inputted generated data points

for(i in 1:numPts) {
    N[i] ~ poisson(norm*exp(rate_log[i]));
}

}