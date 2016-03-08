/*
* Tritium Spectrum Model (Generator)
* -----------------------------------------------------
* Copyright: J. A. Formaggio <josephf@mit.edu>
*
* Date: 25 September 2014
* Modified: Feb 17 2016 by MG
*
* Purpose:
*
*		Program will generate a set of sampled data distributed according to the beta decay spectrum of tritium.
*		Program assumes Project-8 measurement (frequency) and molecular tritium as the source.
*		Spectrum includes simplified beta-function with final state distribution (assuming 0.36 eV gaussian model)
*		Includes broadening due to magnetic field homogeneity, radiative energy loss, Doppler and scattering.
*		T_2 scattering cross-section model implemented.
*		Note that sample events are distributed according to true distribution.
*
*
* Collaboration:  Project 8
*/

functions{

  // Load libraries

  include<-constants;
  include<-func_routines;
  include<-Q_Functions;
  include<-tritium_functions;

  // Finds a simplex of isotopolog fractional composition values in the form (f_T2,f_HT,f_DT, f_atomic) given parameters epsilon and kappa

  vector find_composition(real epsilon, real kappa)
  {
    vector[3] composition;

    composition[1] <- (2.0*epsilon - 1.0);
    composition[2] <- (2.0*(1.0-epsilon)*kappa)/(1+kappa);
    composition[3] <- (2.0*(1.0-epsilon))/(1+kappa);
    return composition;
  }

}

data {

  //   Number of samples to generate (to get event statistics correct)
  int nGenerate;
  int nChains;

  //Mass ordering:
  //if MassHierarchy = 1, normal hierarchy (delta_m31>0)
  //if MassHierarchy = -1, inverted hierarchy (delta_m31<0)
  int MassHierarchy;

  //   Number of neutrinos and mixing parameters
  int nFamily;

  // vector[nFamily] m_nu;
  // simplex[nFamily] U_PMNS;
  real meas_delta_m21;
  real meas_delta_m32_NH;
  real meas_delta_m32_IH;

  real meas_sin2_th12;
  real meas_sin2_th13_NH;
  real meas_sin2_th13_IH;

  real lightest_neutrino_mass;

  //   Primary magnetic field (in Tesla)

  real<lower=0> BField;
  real BFieldError_fluct;

  //   Range for fits (in eV)
  real<lower=0 > minKE;
  real<lower=minKE> maxKE;

  // //   Endpoint of tritium, in eV
  //
  // real<lower=minKE,upper=maxKE> QValue;
  // real<lower=0> sigmaQ;

  //  Cross-section of e-T2 , in meter^-2

  vector[2] xsec_avekin;
  vector[2] xsec_bindkin;
  vector[2] xsec_msq;
  vector[2] xsec_Q;

  //  Conditions of the experiment and measurement

  real number_density;			//  Tritium number density (in meter^-3)
  // real temperature;				//  Temperature of gas (in Kelvin)
  real effective_volume;		        //  Effective volume (in meter^3)
  real measuring_time;			//  Measuring time (in seconds)

  //  Background rate

  real background_rate_mean;			//  Background rate in Hz/eV

  //  Clock and filter information

  real fBandpass;
  real fclockError;
  int  fFilterN;
  // real fclock;

  // Endpoint model input from feature/MH_Talia (Q_generator.stan)

  real T_set;      //Average temperature of source gas in Kelvin
  // real deltaT_calibration;    //Temperature uncertainty due to calibration (K)
  real deltaT_fluctuation;    //Temperature uncertainty due to fluctuations (K)
  real deltaT_rot;    //Temperature uncertainty due to unaccounted for higher rotational states (K)

  int num_J;     // Number of rotational states to be considered (10)
  real lambda_set;    //Average fraction of T2 component of source in ortho (odd rotation) state
  real delta_lambda; //Uncertainty in (lambda = sum(odd-rotation-state-coefficients))

  int num_iso;    //Number of isotopologs under consideration
  vector[num_iso] Q_T_molecule_set;          // Best-estimate endpoint values for tritium molecule (T2, HT, DT)
  real Q_T_atom_set;          // Best-estimate endpoint values for atomic tritium

  real epsilon_set;   // Average fractional activity of source gas compared to pure T_2
  real kappa_set;     // Average ratio of HT to DT
  real eta_set;       // Average proportion of atomic tritium

  // real delta_epsilon; //Uncertainty in fractional activity of source gas compared to pure T_2
  // real delta_kappa; //Uncertainty in ratio of HT to DT
  // real delta_theory; //Uncertainty in composition fraction of non-T (eta = 1.0 --> no T, eta = 0.0 --> all T)


}


transformed data {

  real s12;
  real s13;
  real m1;
  real m2;
  real m3;
  real dm21;
  real dm31;
  real dm32;
  vector[nFamily] m_nu;
  vector[nFamily] U_PMNS;


  real minFreq;
  real maxFreq;
  real fclock;


  //Composition of the gas
  simplex[num_iso] composition;

  vector<lower=0.0>[num_iso] mass_s;

  dm21 <- meas_delta_m21;
  s12 <- meas_sin2_th12;
  if (MassHierarchy == 1)
  {
    dm32 <- meas_delta_m32_NH;
    dm31 <- meas_delta_m32_NH + meas_delta_m21;
    m_nu[1] <- lightest_neutrino_mass;
    m_nu[2] <- sqrt(dm21 + square(m_nu[1]));
    m_nu[3] <- sqrt(dm31 + square(m_nu[1]));
    s13 <- meas_sin2_th13_NH;
  }
  else if (MassHierarchy == -1)
  {
    dm32 <- meas_delta_m32_IH;
    dm31 <- meas_delta_m32_IH + meas_delta_m21;
    m_nu[3] <- lightest_neutrino_mass;
    m_nu[1] <- sqrt(-dm31 + square(m_nu[3]));
    m_nu[2] <- sqrt(-dm32 + square(m_nu[3]));
    s13 <- meas_sin2_th13_IH;
  }
  U_PMNS <- get_U_PMNS(nFamily,s12,s13);

  minFreq <- get_frequency(maxKE, BField);
  maxFreq <- get_frequency(minKE, BField);

  fclock <- 0.;

  if (fBandpass > (maxFreq-minFreq)) {
    print("Bandpass filter (",fBandpass,") is greater than energy range (",maxFreq-minFreq,").");
    print("Consider enlarging energy region.");
  }

  //Transformed Data from feature/MH_Talia (Q_generator.stan)
  // Setting the masses of the tritium species

  mass_s[1] <- tritium_atomic_mass();
  mass_s[2] <- hydrogen_atomic_mass();
  mass_s[3] <- deuterium_atomic_mass();


  composition <- find_composition(epsilon_set,kappa_set);

}

parameters {

  //Parameters used for the convergence of the distributions
  real uB;
  real uQ1;
  real uQ2;
  real uF;
  // //Parameters for Q_generator
  real uT;
  // real uS;

  //Physical parameters
  real<lower=0.0> eDop;
  real<lower=0.0> duration;
  real<lower=minKE,upper=maxKE> KE;

  real<lower=0.0, upper=1.0> lambda;
  real<lower=minKE, upper=maxKE> Q;
}

transformed parameters{

  //Neutrino mass
  real<lower=0> neutrino_mass;
  //Magnetic field
  real<lower=0> MainField;
  //Cross-section calculations
  real beta;
  real xsec;
  real<lower=0> scatt_width;
  real rad_width;
  real tot_width;
  real sigma_freq;
  // Molecular stuff from Talia
  real<lower=0.0> sigmaT;     // Total temperature variation (K)
  real<lower=0.0> temperature;   // Temperature of source gas (K)

  // real epsilon;
  // real kappa;
  // real eta;

  // vector[num_iso] Q;
  real df;
  real frequency;
  //

  //
  real freq_recon;
  // // real freq_temp;
  //
  real kDoppler;
  real KE_shift;
  //
  real activity;
  real signal_fraction;
  real norm_spectrum;
  real spectrum_shape;
  real spectrum;
  //
  // // Q_generator from feature/MH_Talia
  //
  //
  // real<lower=0.0> Q_avg;             // Best estimate for value of Q (eV)
  // real<lower=0.0> sigma_avg;         // Best estimate for value of sigmaQ (eV)
  real<lower=0.0> p_squared;         // (Electron momentum)^2 at the endpoint
  vector<lower=0.0>[num_iso] sigma_0;
  // // // vector<lower=0.0>[num_iso] sigma;
  // //
  real<lower=0> Q_mol;
  real<lower=0> sigma_mol;
  real<lower=0> sigma_atom;
  //
  real<lower=0> Q_mol_random;
  real<lower=0> Q_atom_random;


  real sigma_theory;

  // real signal_rate;




  // Determine effective mass to use from neutrino mass matrix

  neutrino_mass <- sqrt(dot_self(U_PMNS .* m_nu));

  // Obtain magnetic field (with prior distribution)
  MainField <- vnormal_lp(uB, BField, BFieldError_fluct);

  // Temperature of system
  // sigmaT <- sqrt(square(deltaT_calibration) + square(deltaT_fluctuation));
  sigmaT <- deltaT_fluctuation;
  temperature <- vnormal_lp(uT, T_set, sigmaT);

  // Calculate scattering length, radiation width, and total width;
  //The total cross-section is equal to the cross-section of each species, weighted by their relative composition
  // Here we are considering that the ionization cross-section for each molecular tritium {HT, DT, TT} is the same.
  beta <- get_velocity(KE);
  // print(KE);
  xsec <- 0.; //initialize cross section
  xsec <- xsec + (1-eta_set) * xsection(KE,  xsec_avekin[1], xsec_bindkin[1], xsec_msq[1], xsec_Q[1]);//adding the cross-section with modelucar tritium
  xsec <- xsec + (eta_set) * xsection(KE,  xsec_avekin[2], xsec_bindkin[2], xsec_msq[2], xsec_Q[2]);//adding the cross-section with atomic tritium
  scatt_width <- number_density * c() * beta * xsec;
  // print(scatt_width, number_density , c() , beta , xsec);

  rad_width <- cyclotron_rad(MainField);
  tot_width <- (scatt_width + rad_width);
  sigma_freq <- (scatt_width + rad_width) / (4. * pi());//LOOK!

  // Composition and purity of gas system
  // epsilon_set <- 0.5 * (1.0 + composition[1]);
  // kappa_set <- composition[3] / composition[2];
  // composition <- find_composition(epsilon,kappa); //cannot use this since composition is a parameter

  // Find standard deviation of endpoint distribution (eV), given normally distributed input parameters.

  for (i in 1:num_iso) {
    p_squared <- 2.0 * Q_T_molecule_set[i] * m_electron();
    sigma_0[i] <- find_sigma(temperature, p_squared, mass_s[i], num_J, lambda); //LOOK!
  }

  // sigma_theory <- vnormal_lp(uS, 0. , delta_theory);

  //  Take averages of Q and sigma values of molecule

  Q_mol <- sum(composition .* Q_T_molecule_set);
  sigma_mol <- sqrt(sum(composition .* sigma_0 .* sigma_0)); // * (1. + sigma_theory);

  //  Find sigma of atomic tritium

  sigma_atom <- find_sigma(temperature, 2.0 * Q_T_atom_set * m_electron(), 0., 0, 0.);

  // Get a random value of the endpoint for each molecular and atomic tritium

  Q_mol_random <- vnormal_lp(uQ1, Q_mol,sigma_mol);
  Q_atom_random <- vnormal_lp(uQ2, Q_T_atom_set,sigma_atom);


  // Calculate frequency dispersion

  frequency <- get_frequency(KE, MainField);

  df <- vnormal_lp(uF, 0.0, sigma_freq);

  freq_recon <- frequency + df - fclock;

  // Calculate Doppler effect from tritium atom/molecule motion

  // Determine total rate from activity for the molecular tritium
  // activity <- 0.;
  // for (j in 1:num_iso){
  //   activity <- activity + (1-eta_set)*composition[j] * tritium_rate_per_eV() * beta_integral(Q_T_molecule_set[j], neutrino_mass, minKE) * number_density * effective_volume / (tritium_halflife() / log(2.) );
  // }
  // activity <- activity + (eta_set) * tritium_rate_per_eV() * beta_integral(Q_T_atom_set, neutrino_mass, minKE) * number_density * effective_volume / (tritium_halflife() / log(2.) );
  activity <-  tritium_rate_per_eV() * number_density * effective_volume / (tritium_halflife() / log(2.) );
  norm_spectrum <-activity * measuring_time;
  signal_fraction <- activity/(activity + background_rate_mean);



  spectrum <- 0;
  for (i in 1:num_iso){

    kDoppler <-  m_electron() * beta * sqrt(eDop / mass_s[i]);
    KE_shift <- KE + kDoppler;
    //
    // //  Distribute Q value from average
    //
    // // Determine signal and background rates from beta function and background level
    //
    spectrum_shape <- spectral_shape(KE, Q_mol_random, U_PMNS, m_nu);
    spectrum <- spectrum + (1.- eta_set) * composition[i] * norm_spectrum * spectrum_shape;
    // print(spectrum , (1.- eta_set) , composition[i] , norm_spectrum , spectrum_shape);
  }



  // Determine signal and background rates from beta function and background level

  spectrum_shape <- spectral_shape(KE, Q_atom_random, U_PMNS, m_nu);
  spectrum <- spectrum + eta_set * norm_spectrum * spectrum_shape;

  // Adding the background to the spectrum
  spectrum <- spectrum + background_rate_mean * measuring_time;



}

model {

  // print(minKE, maxKE,lambda_set,epsilon_set,kappa_set,eta_set);
  // print("KE");
  KE ~ uniform(minKE,maxKE);

  # Thermal Doppler broadening of the tritium source
  //
  eDop ~ gamma(1.5,1./(k_boltzmann() * temperature));
  //
  // # Frequency broadening from collision and radiation

  duration ~ exponential(scatt_width);

  // # Effect of filter in cleaning data
  //
  // // freq_recon ~ filter(0., fBandpass, fFilterN);
  // freq_recon ~ uniform(minFreq,maxFreq);



  // print("lambda");
  // Find lambda distribution
  // lambda ~ normal(lambda_set, delta_lambda);
  // Find composition distribution
  // epsilon ~ normal(epsilon_set, delta_epsilon);
  // kappa ~ normal(kappa_set, delta_kappa);

  // Q ~ normal(Q_values, sigma);

  // # Otherwise set to flat distribution if nGenerate is negative
  // if (nGenerate >= 0) increment_log_prob(rate_log);

  // Set mixture of molecular and atomic tritium, if needed
  //
  increment_log_prob(log_sum_exp(log(eta_set) + normal_log(Q, Q_mol, sigma_mol),
                                 log1m(eta_set) + normal_log(Q, Q_T_atom_set, sigma_atom)));

}

generated quantities {

  // int isOK;
  int nData;
  // int  events;
  real freq_data;
  real time_data;
  real spectrum_data;
  real KE_recon;

  nData <- nGenerate;
  //
  // #   Simulate duration of event and store frequency and reconstructed kinetic energy
  //
  time_data <- duration;
  //
  freq_data <- freq_recon;
  //
  KE_recon <- get_kinetic_energy(frequency+df, MainField);
  //
  // # Compute the number of events that should be simulated for a given frequency/energy.  Assume Poisson distribution.
  //
  spectrum_data <- spectrum;
  //
  // events <- poisson_rng(spectrum_data / max(abs(nGenerate*nChains),nChains) );

  # Tag events that are below DC in analysis

  // isOK <- (freq_data > 0.);

}
