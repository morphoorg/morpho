/*
* Tritium Spectrum Model (Analysis)
* -----------------------------------------------------
* Copyright: J. A. Formaggio <josephf@mit.edu>
*
* Date: 25 March 2015
* Modified: Feb 17 2016 by MG
*
* Purpose:
*
*		Program will analyze a set of generated data distributed according to the beta decay spectrum of tritium.
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

  //   Number of neutrinos and mixing parameters
  //if MassHierarchy = 1, normal hierarchy (delta_m31>0)
  //if MassHierarchy = -1, inverted hierarchy (delta_m31<0)
  int MassHierarchy;
  real neutrino_mass_limit;

  int nFamily;
  real meas_delta_m21;
  real meas_delta_m32_NH;
  real meas_delta_m32_IH;

  real meas_sin2_th12;
  real meas_sin2_th13_NH;
  real meas_sin2_th13_IH;

  real meas_delta_m21_err;
  real meas_delta_m32_NH_err;
  real meas_delta_m32_IH_err;

  real meas_sin2_th12_err;
  real meas_sin2_th13_NH_err;
  real meas_sin2_th13_IH_err;

  //   Primary magnetic field (in Tesla)

  real<lower=0> BField;
  real BFieldError;

  //   Range for fits (in Hz)

  real<lower=0.0> minKE;
  real<lower=minKE> maxKE;

  //  Cross-section of e-T2 , in meter^-2

  // vector[2] xsec_avekin;
  // vector[2] xsec_bindkin;
  // vector[2] xsec_msq;
  // vector[2] xsec_Q;

  //  Conditions of the experiment and measurement


  real number_density;			//  Tritium number density (in meter^-3)
  real effective_volume;		        //  Effective volume (in meter^3)
  real measuring_time;			//  Measuring time (in seconds)

  //  Background rate

  real background_rate_mean;			//  Background rate in Hz/eV

  //  Clock and filter information

  real fBandpass;
  real fclockError;
  int  fFilterN;

  //  Input data (from generated sample)

  int nBinTime;
  vector[nBinTime] time_data;
  int n_time_data[nBinTime];
  int nBinEvents;
  vector[nBinEvents] freq_data;
  int n_events[nBinEvents];


  // Endpoint model input from feature/MH_Talia (Q_generator.stan)

  real T_set;      //Average temperature of source gas in Kelvin
  real deltaT_calibration;    //Temperature uncertainty due to calibration (K)
  real deltaT_fluctuation;    //Temperature uncertainty due to fluctuations (K)
  real deltaT_rot;    //Temperature uncertainty due to unaccounted for higher rotational states (K)

  int num_J;     // Number of rotational states to be considered (10)
  real lambda_set;    //Average fraction of T2 component of source in ortho (odd rotation) state
  real delta_lambda; //Uncertainty in (lambda = sum(odd-rotation-state-coefficients))

  int num_iso;    //Number of isotopologs under consideration
  vector[num_iso] Q_T_molecule_set;          // Best-estimate endpoint values for tritium molecule (T2, HT, DT)
  vector[num_iso] eQ_T_molecule_set;
  real Q_T_atom_set;          // Best-estimate endpoint values for atomic tritium
  real eQ_T_atom_set;          // Best-estimate endpoint values for atomic tritium

  real epsilon_set;   // Average fractional activity of source gas compared to pure T_2
  real kappa_set;     // Average ratio of HT to DT
  real eta_set;       // Average proportion of atomic tritium
  real err_epsilon_set;   // Average fractional activity of source gas compared to pure T_2
  real err_kappa_set;     // Average ratio of HT to DT
  real err_eta_set;       // Average proportion of atomic tritium
  real delta_theory; //Uncertainty in composition fraction of non-T (eta = 1.0 --> no T, eta = 0.0 --> all T)

}

transformed data {

  real minFreq;
  real maxFreq;
  real fclock;
  vector<lower=0.0>[num_iso] mass_s;


  minFreq <- get_frequency(maxKE, BField);
  maxFreq <- get_frequency(minKE, BField);

  fclock <- 0.;

  if (fBandpass > (maxFreq-minFreq)) {
    print("Bandpass filter (",fBandpass,") is greater than energy range (",maxFreq-minFreq,").");
    print("Consider enlarging energy region.");
  }

  // print("Approximate activity = ",tritium_rate_per_eV() * beta_integral(KE, 0., minKE) * number_density * effective_volume / tritium_halflife() / log(2.) * measuring_time);

  // print("Approximate rate (Hz) = ",tritium_rate_per_eV() * beta_integral(KE, 0., minKE) * number_density * effective_volume / tritium_halflife() / log(2.));

  // print(num_iso);
  mass_s[1] <- tritium_atomic_mass();
  mass_s[2] <- hydrogen_atomic_mass();
  mass_s[3] <- deuterium_atomic_mass();

}

parameters {

  real<lower=1.e-5,upper=1.e-4> background_rate;
  real<lower=0.5, upper=1.5> mu_tot;
  real<lower=0.,upper=4.> lightest_neutrino_mass;

  real<lower=0.5,upper=1.5> uB;
  real<lower=-1,upper=1> uF;
  real<lower=minKE,upper=maxKE> uQ;
  real<lower=-1,upper=1> uS;


  real udm21;
  real udm32;
  real us12;
  real us13;
  real<lower=0.0> eDop;
  real<lower=1e4,upper=10e4> scatt_width;
  real<lower=0, upper=30000> n0_timeData;

  real<lower=20,upper=40> Tparam1;
  // real Tparam2;
  real<lower=0, upper=1> lambda_param;
  real<lower=0, upper=1> epsilon_param;
  real<lower=0, upper=1> kappa_param;
  real<lower=0, upper=1> eta_param;
}

transformed parameters{

  // Oscillations parameters
  real dm21;
  real dm32;
  real dm31;
  real s12;
  real s13;
  vector<lower = 0.>[nFamily] m_nu;
  vector[nFamily] U_PMNS;
  real<lower = 0.> neutrino_mass;
  // Main Field
  real<lower=0> MainField;

  // parameters for the i=uncertainty on the frequency
  real rad_width;
  real tot_width;
  real sigma_freq;

  // temperrature
  // real<lower=20., upper=40.> T0;     // Average of temperature distribution, given temp calibration (K)
  real<lower=20., upper=40.> temperature;   // Temperature of source gas (K)
  real<lower=0.0> deltaT_total;      // Used only for calculation of delta_sigma, as check (K)

  //gas composition parameters
  real<lower=0.0> lambda;   // Fraction of T2 component of source in ortho (odd rotation) state
  real<lower=0.0> epsilon;  // Fractional activity of source gas compared to pure T_2
  real<lower=0.0> kappa;    // Ratio of HT to DT
  real<lower=0.0,upper=1.0> eta;      // Composition fraction of T (eta = f_T/(f_T2+f_HT+f_DT))
  vector[num_iso] composition; //Simplex of fractional composition of each isotopolog: (f_T2,f_HT,f_DT, f_T)
  vector[num_iso] composition_set; //Simplex of fractional composition of each isotopolog: (f_T2,f_HT,f_DT, f_T)

  // Q values uncertainty and definitions
  real<lower=0.0> p_squared;         // (Electron momentum)^2 at the endpoint
  real<lower=0.0> Q_mol; //average Q molecular
  real<lower=0.0> sigma_mol; //
  vector<lower=0.0>[num_iso] sigma_0; //Fluctuations on Q molecular
  real<lower=0.0> sigma_atom;     //Fluctuations on Q atomic
  vector[num_iso] Q_T_molecule;          // Best-estimate endpoint values for tritium molecule (T2, HT, DT)
  real Q_T_atom;          // Best-estimate endpoint values for tritium molecule (T2, HT, DT)
  real sigma_theory;

  // Rate calculation
  vector[nBinEvents] rate;

  real activity;
  real rate_log;
  real norm_density;
  real signal_fraction;

  //
  real KE;
  vector[nBinEvents] frequency;
  real df;

  real kDoppler;
  real KE_shift;
  // real Q0;
  real Q;




  // real<lower=0.0> sigma_floating;         // Best estimate, from theory, for standard deviation of Q distribution (eV)
  real delta_sigma;       // Uncertainty (1 stdev) in estimate of sigma (sigma_avg), from theory

  // Priors on the neutrino mixin parameters and mass differences
  dm21 <- vnormal_lp(udm21,meas_delta_m21,meas_delta_m21_err);
  s12 <- fabs(vnormal_lp(us12, meas_sin2_th12,meas_sin2_th12_err));

  if (MassHierarchy == 1)
  {
    dm32 <- vnormal_lp(udm32, meas_delta_m32_NH,meas_delta_m32_NH_err);
    s13 <- fabs(vnormal_lp(us13,meas_sin2_th13_NH,meas_sin2_th13_NH_err));
    dm31 <- meas_delta_m32_NH + meas_delta_m21;
    m_nu[1] <- lightest_neutrino_mass;
    m_nu[2] <- sqrt(fabs(dm21 + square(m_nu[1])));
    m_nu[3] <- sqrt(fabs(dm31 + square(m_nu[1])));
  }
  else if (MassHierarchy == -1)
  {
    dm32 <- vnormal_lp(udm32,meas_delta_m32_IH,meas_delta_m32_IH_err);
    s13 <- fabs(vnormal_lp(us13,meas_sin2_th13_IH,meas_sin2_th13_IH_err));
    dm31 <- meas_delta_m32_IH + meas_delta_m21;
    m_nu[3] <- lightest_neutrino_mass;
    m_nu[1] <- sqrt(fabs(-dm31 + square(m_nu[3])));
    m_nu[2] <- sqrt(fabs(-dm32 + square(m_nu[3])));
  }
  U_PMNS <- get_U_PMNS(nFamily,fabs(s12),fabs(s13));

  neutrino_mass <- fabs(dot_product(U_PMNS,m_nu));

  //   Obtain magnetic field (with prior distribution)

  MainField <- vnormal_lp(uB, BField, BFieldError);

  //   Calculate scattering length, radiation width, and total width;

  rad_width <- cyclotron_rad(MainField);
  tot_width <- (scatt_width + rad_width);
  sigma_freq <- (scatt_width + rad_width) / (4. * pi());

  #  Determining endpoint
  # Here is where the model from Talia comes

  deltaT_total <- pow(pow(deltaT_calibration, 2) + pow(deltaT_fluctuation, 2), 0.5);
  temperature <- vnormal_lp(Tparam1, T_set, deltaT_total);

  //
  lambda <- vnormal_lp(lambda_param, lambda_set, delta_lambda);
  epsilon <- vnormal_lp(epsilon_param, epsilon_set, err_epsilon_set);
  kappa <- vnormal_lp(kappa_param, kappa_set, err_kappa_set);

  if (err_eta_set != 0.0){
    eta <- vnormal_lp(eta_param, eta_set, err_eta_set);
  }
  else eta <- eta_set;
  // print(eta);
  //
  composition <- find_composition(epsilon, kappa);
  composition_set <- find_composition(epsilon_set, kappa_set);


  // Find standard deviation of endpoint distribution (eV), given normally distributed input parameters.

  for (i in 1:num_iso) {
    p_squared <- 2.0 * Q_T_molecule_set[i] * m_electron();
    sigma_0[i] <- find_sigma(temperature, p_squared, mass_s[i], num_J, lambda); //LOOK!
    Q_T_molecule[i] <- vnormal_lp(uQ,Q_T_molecule_set[i],sigma_0[i]);
  }

  sigma_theory <- vnormal_lp(uS, 0. , delta_theory);

  //  Take averages of Q and sigma values of molecule

  Q_mol <- sum(composition .* Q_T_molecule);
  sigma_mol <- sqrt(sum(composition .* sigma_0 .* sigma_0)) * (1. + sigma_theory);

  //  Find sigma of atomic tritium

  sigma_atom <- find_sigma(temperature, 2.0 * Q_T_atom_set * m_electron(), 0., 0, 0.);
  Q_T_atom <- vnormal_lp(uQ,Q_T_atom_set,sigma_atom);

  // Determine total rate from activity
  for (i in 1:nBinEvents)
  {
    rate[i] <- 0.;
  }

  df <- vnormal_lp(uF, 0.0, sigma_freq);

    // Determine signal and background rates from beta function and background level
  activity <- 0.;
  // for (j in 1:num_iso){
  //
  //   activity <- activity + (1-eta)*composition[j] * tritium_rate_per_eV() * beta_integral(Q_T_molecule[j], neutrino_mass, minKE) * number_density * effective_volume / (tritium_halflife() / log(2.) );
  // }
  // activity <- activity + (eta) * tritium_rate_per_eV() * beta_integral(Q_T_atom, neutrino_mass, minKE) * number_density * effective_volume / (tritium_halflife() / log(2.) );
  activity <- activity + (eta) * tritium_rate_per_eV() * number_density * effective_volume / (tritium_halflife() / log(2.) );

  norm_density <- mu_tot * activity * measuring_time;
  signal_fraction <- activity/(activity + background_rate);

  for (i in 1:nBinEvents){
    frequency[i] <- freq_data[i] - df + fclock;
    KE <- get_kinetic_energy(frequency[i], MainField);

    // for (j in 1:num_iso){
    //
    //   kDoppler <-  m_electron() * get_velocity(KE) * sqrt(eDop / mass_s[j]);
    //
    //   KE_shift <- KE - kDoppler;
    //
    //   rate_log <- signal_to_noise_log(KE_shift, Q_T_molecule[j], U_PMNS, m_nu , minKE, maxKE, signal_fraction);
    //   rate[i] <- rate[i] + (1-eta) * composition[j] * total_rate * exp(rate_log);
    // }

    KE <- get_kinetic_energy(frequency[i], MainField);
    // rate_log <- signal_to_noise_log(KE, Q_T_atom, U_PMNS, m_nu , minKE, maxKE, signal_fraction);
    // rate[i] <- rate[i] + (eta) * total_rate * exp(rate_log);
    // print(frequency[i],rate[i]);
  }



  // kDoppler <-  m_electron() * get_velocity(KE) * sqrt(eDop / tritium_molecular_mass());

  // KE_shift <- KE - kDoppler;

  //   Determine signal and background rates from beta function and background level



 // print("loop");
}

model {

  // mu_tot ~ uniform(0.5,1.);

  // background_rate ~ normal(background_rate_mean,)

  #  Thermal Doppler broadening of the tritium source

  eDop ~ gamma(1.5,1./(k_boltzmann() * temperature));
  //
  for (i in 1:nBinTime)
  {
    if(n_time_data[i]!=0)
    {
      n_time_data[i] ~ normal( n0_timeData * exp( - time_data[i] * scatt_width ) , sqrt( n_time_data[i]*1. ) );
    }
  }
  //
  mu_tot ~ uniform(0.5 ,1.5);
  for (i in 1:nBinEvents)
  {
    if(rate[i]!=0)
    {
      increment_log_prob(poisson_log(n_events[i],rate[i]));
      // n_events[i] ~ poisson(rate[i]);
    }
  }



}

generated quantities {

}
