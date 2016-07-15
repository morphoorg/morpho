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


functions{

    // Load libraries

    include_functions<-func_routines
    include_functions<-MH_Functions

}

data{

    // Neutrino mixing parameters
    real  meas_delta_m21;        // Best known value of delta_m2^2-delta_m1^2 in eV^2
    real  meas_delta_m21_err;    // Error on delta_m2^2-delta_m1^2 in eV^2
    real  meas_delta_m32;        // Best known value of delta_m3^2-delta_m2^2 in eV^2
    real  meas_delta_m32_err;    // Error on delta_m3^2-delta_m2^2 in eV^2
    
    real  meas_sin2_th12;         // Best known value of sin squared of 2*theta_12 (radians)
    real  meas_sin2_th12_err;    // Error on sin squared of 2*theta_12
    
    real  meas_sin2_th13_NH;     // Best known value of sin squared of 2*theta_13 for normal hierarchy
    real  meas_sin2_th13_NH_err; // Error on sin squared of 2*theta_13 for normal hierarchy
    real  meas_sin2_th13_IH;     // Same for inverted hierarchy
    real  meas_sin2_th13_IH_err;

    real  min_mass_fixed;        // Inputted value chosen as lightest mass (between 0.0 and 0.5 eV)
    
    real<lower=0 > minKE;        // Bounds on possible beta-decay spectrum kinetic energies in eV
    real<lower=minKE> maxKE;
    real Q;                      // Endpoint of beta-decay spectrum in eV - should be between minKE and maxKE
    real signal_fraction;        // Fraction of events that can be described as signal (as opposed to background)

    int nGenerate;               // Number of points to be generated

    int MH;                      // Either 0 (normal hierarchy) or 1 (inverted hierarchy)

}

parameters{

    real<lower=minKE, upper=maxKE> KE;          // Kinetic energies of electrons from beta decay in eV
}

transformed parameters {

    real<lower=0., upper =1.> meas_sin2_th13;
    vector<lower=0.0>[3] sUe_fixed;     // Squares of PMNS matrix elements U_e, calculated using fixed mixing angles
    vector<lower=0.0>[3] nu_mass_fixed; // Neutrino masses calculated with fixed mixing parameters, asumming one MH
    real rate_log;                // Beta decay spectrum generated assuming one MH

    if (MH == 0){
        nu_mass_fixed <- MH_masses(min_mass_fixed, meas_delta_m21, meas_delta_m32_NH, MH);
        meas_sin2_th13 <- meas_sin2_th13_NH;}
    if (MH == 1){
        nu_mass_fixed <- MH_masses(min_mass_fixed, meas_delta_m21, meas_delta_m32_IH, MH);
        meas_sin2_th13 <- meas_sin2_th13_IH;}
        
    
    sUe_fixed <- matrix_elements(meas_sin2_th12, meas_sin2_th13);

    rate_log <- signal_to_noise_log(KE, Q, sUe_fixed, nu_mass_fixed, minKE, maxKE, signal_fraction);

}

model{

    KE ~ uniform(minKE,maxKE);

}

generated quantities {

    int nData;
    real KE_data;
    real spectrum_data;

    nData <- nGenerate;
    KE_data <- KE;
    spectrum_data <- rate_log;

}
