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
  real BFieldError_fluct;
  real BFieldError_calib;

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
  real background_rate_err;			//  Background rate in Hz/eV

  //  Clock and filter information

  real fBandpass;
  real fclockError;
  int  fFilterN;

  //  Input data (from generated sample)

  int nBinTime;
  vector[nBinTime] time_data;
  int n_time_data[nBinTime];
  int nBinSpectrum;
  vector[nBinSpectrum] freq_data;
  int n_spectrum_data[nBinSpectrum];


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

  real fclock;
  vector<lower=0.0>[num_iso] mass_s;
  real dFreq_bin;
  real minFreq;
  real maxFreq;

  dFreq_bin <- (freq_data[nBinSpectrum] - freq_data[1])/nBinSpectrum;
  minFreq <- freq_data[1];
  maxFreq <- freq_data[nBinSpectrum];


  fclock <- 0.;

  if (fBandpass > (maxFreq-minFreq)) {
    print("Bandpass filter (",fBandpass,") is greater than energy range (",maxFreq-minFreq,").");
    print("Consider enlarging energy region.");
  }

  // print("Approximate activity = ",tritium_rate_per_eV() * beta_integral(KE, 0., minKE) * number_density * effective_volume / tritium_halflife() / log(2.) * measuring_time);

  // print("Approximate rate (Hz) = ",tritium_rate_per_eV() * beta_integral(KE, 0., minKE) * number_density * effective_volume / tritium_halflife() / log(2.));

  mass_s[1] <- tritium_atomic_mass();
  mass_s[2] <- hydrogen_atomic_mass();
  mass_s[3] <- deuterium_atomic_mass();

}

parameters {

  real<lower=0.5, upper=1.5> mu_tot;
  real<lower=0.,upper=100.> lightest_neutrino_mass;

  real uB;
  real uBG;
  real uF;
  real uQ1;
  real uQ2;
  real uS;


  real udm21;
  real udm32;
  real us12;
  real us13;
  real<lower=0.0> eDop;
  real<lower=1e4,upper=10e4> scatt_width;
  real<lower=100, upper=1000> n0_timeData;

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
  real<lower=0., upper =1.> s12;
  real<lower=0., upper =1.> s13;
  vector<lower = 0.>[nFamily] m_nu;
  vector[nFamily] U_PMNS;
  real<lower = 0.> neutrino_mass;

  // Main Field
  real<lower=0> MainField;
  real BFieldError_tot;//total error on the B field (fluctuations + calbration)

  // Width of the bins
  real widthBin;

  // parameters for the i=uncertainty on the frequency
  real rad_width;
  real tot_width;
  real sigma_freq;

  // temperature
  // real<lower=20., upper=40.> T0;     // Average of temperature distribution, given temp calibration (K)
  real<lower=20., upper=40.> temperature;   // Temperature of source gas (K)
  real<lower=0.0> deltaT_total;      // Used only for calculation of delta_sigma, as check (K)
  //
  //   //gas composition parameters
  real<lower=0.0, upper=1.0> lambda;   // Fraction of T2 component of source in ortho (odd rotation) state
  real<lower=0.0> epsilon;  // Fractional activity of source gas compared to pure T_2
  real<lower=0.0> kappa;    // Ratio of HT to DT
  real<lower=0.0,upper=1.0> eta;      // Composition fraction of T (eta = f_T/(f_T2+f_HT+f_DT))
  simplex[num_iso] composition; //Simplex of fractional composition of each isotopolog: (f_T2,f_HT,f_DT, f_T)
  simplex[num_iso] composition_set; //Simplex of fractional composition of each isotopolog: (f_T2,f_HT,f_DT, f_T)
  //
  //   // Q values uncertainty and definitions
  real<lower=0.0> p_squared;         // (Electron momentum)^2 at the endpoint
  real<lower=minKE,upper=maxKE> Q_mol; //average Q molecular
  real<lower=0.0> sigma_mol; //
  vector<lower=0.0>[num_iso] sigma_0; //Fluctuations on Q molecular
  real<lower=0.0> sigma_atom;     //Fluctuations on Q atomic
  vector<lower=minKE,upper=maxKE>[num_iso] Q_T_molecule;          // Best-estimate endpoint values for tritium molecule (T2, HT, DT)
  real<lower=minKE,upper=maxKE>  Q_T_atom;          // Best-estimate endpoint values for tritium molecule (T2, HT, DT)
  real sigma_theory;

  // Rate calculation
  real background_rate;
  vector[nBinSpectrum] n_spectrum_recon; //reconstructed content of spectrum bins
  real activity;
  real spectrum;
  real spectrum_shape;
  real norm_density;
  real signal_fraction;
  real beta;

  //
  real KE;
  vector[nBinSpectrum] frequency;
  real df;

  real kDoppler;
  real KE_shift;
  real Q;
  real delta_sigma;       // Uncertainty (1 stdev) in estimate of sigma (sigma_avg), from theory


  // //////////////////

  // Priors on the neutrino mixin parameters and mass differences
  dm21 <- meas_delta_m21 + vnormal_lp(udm21,0.,meas_delta_m21_err);
  s12 <- fabs(meas_sin2_th12 + vnormal_lp(us12, 0. ,meas_sin2_th12_err));

  if (MassHierarchy == 1)
  {
    dm32 <- meas_delta_m32_NH + vnormal_lp(udm32, 0. ,meas_delta_m32_NH_err);
    s13 <- fabs(meas_sin2_th13_NH + vnormal_lp(us13,0.,meas_sin2_th13_NH_err));
    dm31 <- meas_delta_m32_NH + meas_delta_m21;
    m_nu[1] <- lightest_neutrino_mass;
    m_nu[2] <- sqrt(fabs(dm21 + square(m_nu[1])));
    m_nu[3] <- sqrt(fabs(dm31 + square(m_nu[1])));
  }
  else if (MassHierarchy == -1)
  {
    dm32 <- meas_delta_m32_IH + vnormal_lp(udm32, 0.,meas_delta_m32_IH_err);
    s13 <- fabs(meas_sin2_th13_IH + vnormal_lp(us13, 0. ,meas_sin2_th13_IH_err));
    dm31 <- meas_delta_m32_IH + meas_delta_m21;
    m_nu[3] <- lightest_neutrino_mass;
    m_nu[1] <- sqrt(fabs(-dm31 + square(m_nu[3])));
    m_nu[2] <- sqrt(fabs(-dm32 + square(m_nu[3])));
  }
  U_PMNS <- get_U_PMNS(nFamily,fabs(s12),fabs(s13));

  neutrino_mass <- sqrt(U_PMNS[1] * pow(m_nu[1],2) +U_PMNS[2] * pow(m_nu[2],2) +U_PMNS[3] * pow(m_nu[3],2) );

  //   Obtain magnetic field (with prior distribution)
  BFieldError_tot <- pow(pow(BFieldError_calib,2)+pow(BFieldError_fluct,2),0.5);
  MainField <- BField + vnormal_lp(uB, 0. , BFieldError_tot);


  // Determine the deltaE of the bin
  widthBin <- fabs((get_kinetic_energy(freq_data[1],MainField) - get_kinetic_energy(freq_data[nBinSpectrum],MainField))/nBinSpectrum);

  //   Calculate scattering length, radiation width, and total width;

  rad_width <- cyclotron_rad(MainField);
  tot_width <- (scatt_width + rad_width);
  sigma_freq <- (scatt_width + rad_width) / (4. * pi());

  #  Determining endpoint
  # Here is where the model from Talia comes

  deltaT_total <- pow(pow(deltaT_calibration, 2) + pow(deltaT_fluctuation, 2), 0.5);
  temperature <- T_set + vnormal_lp(Tparam1, 0. , deltaT_total);
  //
  lambda <- vnormal_lp(lambda_param, lambda_set, delta_lambda);
  epsilon <- vnormal_lp(epsilon_param, epsilon_set, err_epsilon_set);
  kappa <- vnormal_lp(kappa_param, kappa_set, err_kappa_set);
  //
  if (err_eta_set != 0.0){
    eta <- vnormal_lp(eta_param, eta_set, err_eta_set);
    // eta <- eta_set;
  }
  else eta <- eta_set;
  //
  composition <- find_composition(epsilon, kappa);
  composition_set <- find_composition(epsilon_set, kappa_set);
  //
  //
  // // Find standard deviation of endpoint distribution (eV), given normally distributed input parameters.
  //
  for (i in 1:num_iso) {
    p_squared <- 2.0 * Q_T_molecule_set[i] * m_electron();
    sigma_0[i] <- find_sigma(temperature, p_squared, mass_s[i], num_J, lambda); //LOOK!
    Q_T_molecule[i] <- Q_T_molecule_set[i] + vnormal_lp(uQ1 , 0. , sigma_0[i]);
  }

  sigma_theory <-  vnormal_lp(uS, 0. , delta_theory);

  //  Take averages of Q and sigma values of molecule

  Q_mol <- sum(composition .* Q_T_molecule);
  sigma_mol <- sqrt(sum(composition .* sigma_0 .* sigma_0)) * (1. + sigma_theory);

  //  Find sigma of atomic tritium

  sigma_atom <- find_sigma(temperature, 2.0 * Q_T_atom_set * m_electron(), 0., 0, 0.);
  Q_T_atom <- Q_T_atom_set + vnormal_lp(uQ2 , 0. , sigma_atom);

  //////////////////
  // Determine total rate from activity
  // [faux]
  // activity <-  tritium_rate_per_eV() * number_density * effective_volume / (tritium_halflife() / log(2.) );
  // norm_spectrum <-activity * measuring_time;
  // signal_fraction <- activity/(activity + background_rate_mean);
  // [/faux]
  //////////////


  df <- vnormal_lp(uF, 0.0, sigma_freq);

  // Determine signal from beta function and background level
  activity <- tritium_rate_per_eV() * number_density * effective_volume / (tritium_halflife() / log(2.) );


  norm_density <-  mu_tot * activity * measuring_time;
  background_rate <- fabs(background_rate_mean + vnormal_lp(uBG,0. ,background_rate_err));
  signal_fraction <- activity/(activity + background_rate);

  for (j in 1:nBinSpectrum){
    frequency[j] <- freq_data[j] - df + fclock;
    KE <- get_kinetic_energy(frequency[j], MainField);
    beta <- get_velocity(KE);

    spectrum <- 0;
    for (i in 1:num_iso){

      kDoppler <-  m_electron() * beta * sqrt(eDop / mass_s[i]);
      KE_shift <- KE + kDoppler;
      //
      // //  Distribute Q value from average
      //
      // // Determine signal and background rates from beta function and background level
      //
      spectrum_shape <- spectral_shape(KE, Q_mol, U_PMNS, m_nu);
      spectrum <- spectrum + (1.- eta) * composition[i] * norm_density * spectrum_shape;
    }



    // Determine signal and background rates from beta function and background level

    spectrum_shape <- spectral_shape(KE, Q_T_atom, U_PMNS, m_nu);
    spectrum <- spectrum + eta * norm_density * spectrum_shape;

    // Adding the background to the spectrum
    spectrum <- spectrum + background_rate * measuring_time;


    n_spectrum_recon[j] <- spectrum * widthBin;
    if (n_spectrum_recon[j]<0.)
    {
      print(s12,"  ", s13);
      print(n_spectrum_recon[j],"  ", spectrum,"  ", widthBin,"  ",eta ,"  ", norm_density ,"  ", spectrum_shape,"  ",background_rate ,"  ", measuring_time);
    }

  }
  ////////////////////////




}

model {


  // MainField ~ normal(BField, BFieldError_tot);
  // mu_tot ~ uniform(0.5,1.);

  // background_rate ~ normal(background_rate_mean,)

  #  Thermal Doppler broadening of the tritium source

  eDop ~ gamma(1.5,1./(k_boltzmann() * temperature));

  for (i in 1:nBinTime)
  {
    if(n_time_data[i]>0)
    {
      increment_log_prob(poisson_log(n_time_data[i], n0_timeData * exp( - time_data[i] * scatt_width )));
      // print(time_data[i],"  ",n_time_data[i]);
    }
  }
  //
  mu_tot ~ uniform(0.5 ,1.5);

  for (i in 1:nBinSpectrum)
  {
    if(n_spectrum_data[i]>0 )
    {
      increment_log_prob(poisson_log(n_spectrum_data[i],n_spectrum_recon[i]));
      // n_events[i] ~ poisson(rate[i]);
    }
  }



}

generated quantities {


}
