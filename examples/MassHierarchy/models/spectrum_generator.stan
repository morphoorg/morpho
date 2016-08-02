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

    include<-constants;
    include<-func_routines;
    include<-neutrino_mass_functions;
    include<-tritium_functions;
}

data{

    real  min_mass_fixed;        // Inputted value chosen as lightest mass (between 0.0 and 0.5 eV)
    
    real<lower=0 > minKE;        // Bounds on possible beta-decay spectrum kinetic energies in eV
    real<lower=minKE> maxKE;

    real Q;                        // Endpoint of beta-decay spectrum in eV - should be between minKE and maxKE
    //real signal_fraction;        // Fraction of events that can be described as signal (as opposed to background)
    real background_rate_mean;     // In Hz/eV
    real measuring_time;           // In seconds
    real activity;                 // (Molecular tritium) activity

    int MH;                      // Either 0 (normal hierarchy) or 1 (inverted hierarchy)

}

parameters{

    real<lower=minKE, upper=maxKE> KE_data;          // Kinetic energies of electrons from beta decay in eV
}

transformed parameters {

    real<lower=0., upper =1.> meas_sin2_th13;
    vector<lower=0.0>[3] sUe_fixed;     // Squares of PMNS matrix elements U_e, calculated using fixed mixing angles
    vector<lower=0.0>[3] nu_mass_fixed; // Neutrino masses calculated with fixed mixing parameters, asumming one MH
    real spectrum_shape;                // Beta decay spectrum generated assuming one MH
    real spectrum;                      // Accounting for measuring time and background

//    print(MH);

    if (MH == 0){
        nu_mass_fixed <- MH_masses(min_mass_fixed, meas_delta_m21(), meas_delta_m32_NH(), MH);
        meas_sin2_th13 <- meas_sin2_th13_NH();}
    if (MH == 1){
        nu_mass_fixed <- MH_masses(min_mass_fixed, meas_delta_m21(), meas_delta_m32_IH(), MH);
//	print(nu_mass_fixed);
        meas_sin2_th13 <- meas_sin2_th13_IH();}
        
    
    sUe_fixed <- get_U_PMNS(nFamily(), meas_sin2_th12(), meas_sin2_th13);

    spectrum_shape <- spectral_shape(KE_data, Q, sUe_fixed, nu_mass_fixed);
    spectrum <- activity * measuring_time * spectrum_shape + background_rate_mean * measuring_time;
}

model{

    KE_data ~ uniform(minKE+1.,maxKE-1.);
//    increment_log_prob(log(KE_data));


}

generated quantities {

//    real KE_data;
    real spectrum_data;

//    KE_data <- KE;
    spectrum_data <- spectrum;

}