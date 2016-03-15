/*
* MC Neutrino Mass and Beta Decay Model - Generator
* -----------------------------------------------------
* Authors: Talia Weiss <tweiss@mit.edu>
*          J. A. Formaggio <josephf@mit.edu>
*
* Date: 9 July 2015
*
* Purpose:
*
* Generates beta decay spectrum and poisson-distributed data points in Stan assuming either normal or inverted mass hierarchy.
*
*/


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

    real  min_mass_fixed;       // Inputted value chosen as lightest mass (between 0.0 and 0.5 eV)

    real minKE;                 // Bounds on possible beta-decay spectrum kinetic energies in eV
    real maxKE;
    real Q;                     // Endpoint of beta-decay spectrum in eV - should be between minKE and maxKE
    real signal_fraction;       // Fraction of events that can be described as signal (as opposed to background)

    int numPts;                 // Number of points to be generated
    real norm;                  // Temporary normalization for Poisson distribution of spectrum

    int MH;                     // Either 0 (normal hierarchy) or 1 (inverted hierarchy)

}

parameters{

    real<lower=minKE, upper=maxKE> KE;          // Kinetic energies of electrons from beta decay in eV
}

transformed parameters {

    vector<lower=0.0>[3] sUe_fixed;     // Squares of PMNS matrix elements U_e, calculated using fixed mixing angles
    vector<lower=0.0>[3] nu_mass_fixed; // Neutrino masses calculated with fixed mixing parameters, asumming one MH
    real rate_log;                // Beta decay spectrum generated assuming one MH


    sUe_fixed <- matrix_elements(sin_sq_2meas_th12, sin_sq_2meas_th13);
    nu_mass_fixed <- MH_masses(min_mass_fixed, meas_delta_m21, meas_delta_m32, MH);

    rate_log <- signal_to_noise_log(KE, Q, sUe_fixed, nu_mass_fixed, minKE, maxKE, signal_fraction);

}

model{
}

generated quantities {

    int N;      //For each sampling iteration, generating a point based on poisson spread of rate log function

    N <- poisson_rng(exp(rate_log)*norm);
    //print(N);

}
