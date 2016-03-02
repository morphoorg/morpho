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

  real<lower=0 > minKE;
  real<lower=minKE> maxKE;

  //  Cross-section of e-T2 , in meter^-2

  real xsec_avekin;
  vector[2] xsec_bindkin;
  vector[2] xsec_msq;
  vector[2] xsec_Q

  //  Conditions of the experiment and measurement


  real number_density;			//  Tritium number density (in meter^-3)
  real effective_volume;		        //  Effective volume (in meter^3)
  real measuring_time;			//  Measuring time (in seconds)

  //  Background rate

  real background_rate;			//  Background rate in Hz/eV

  //  Clock and filter information

  real fBandpass;
  real fclockError;
  int  fFilterN;

  // Endpoint model input from feature/MH_Talia (Q_generator.stan)

  real T_set;      //Average temperature of source gas in Kelvin
  real deltaT_calibration;    //Temperature uncertainty due to calibration (K)
  real deltaT_fluctuation;    //Temperature uncertainty due to fluctuations (K)
  real deltaT_rot;    //Temperature uncertainty due to unaccounted for higher rotational states (K)

  int num_J;     // Number of rotational states to be considered (10)
  real lambda_set;    //Average fraction of T2 component of source in ortho (odd rotation) state
  real delta_lambda; //Uncertainty in (lambda = sum(odd-rotation-state-coefficients))

  int num_iso;    //Number of isotopologs under consideration
  vector[num_iso] Q_T_molecule;          // Best-estimate endpoint values for tritium molecule (T2, HT, DT)
  vector[num_iso] eQ_T_molecule;
  real Q_T_atom;          // Best-estimate endpoint values for atomic tritium
  real eQ_T_atom;          // Best-estimate endpoint values for atomic tritium

  real epsilon_set;   // Average fractional activity of source gas compared to pure T_2
  real kappa_set;     // Average ratio of HT to DT
  real eta_set;       // Average proportion of atomic tritium
  real err_epsilon_set;   // Average fractional activity of source gas compared to pure T_2
  real err_kappa_set;     // Average ratio of HT to DT
  real err_eta_set;       // Average proportion of atomic tritium
}

transformed data {

  real minFreq;
  real maxFreq;
  real fclock;

  minFreq <- get_frequency(maxKE, BField);
  maxFreq <- get_frequency(minKE, BField);

  fclock <- 0.;

  if (fBandpass > (maxFreq-minFreq)) {
    print("Bandpass filter (",fBandpass,") is greater than energy range (",maxFreq-minFreq,").");
    print("Consider enlarging energy region.");
  }

  print("Approximate activity = ",tritium_rate_per_eV() * beta_integral(QValue, 0., minKE) * number_density * effective_volume / tritium_halflife() / log(2.) * measuring_time);

  print("Approximate rate (Hz) = ",tritium_rate_per_eV() * beta_integral(QValue, 0., minKE) * number_density * effective_volume / tritium_halflife() / log(2.));

}

parameters {

  real<lower=0.,upper=1.> signal_fraction;
  real<lower=0.5, upper=1.5> mu_tot;
  real<lower=0.,upper=4.> lightest_neutrino_mass;

  real uB;
  real uF;
  real uQ0;
  real uQ;


  real udm21;
  real udm32;
  real us12;
  real us13;
  real<lower=0.0> eDop;
  real<lower=3.5e4,upper=10e4> scatt_width;
  real<lower=10000, upper=30000> n0_timeData;

  real Tparam1;
  real Tparam2;
  real lambda_param;
  real epsilon_param;
  real kappa_param;
  real eta_param;
}

transformed parameters{

  real KE;
  real frequency;

  // real signal_rate;
  real<lower=0> MainField;
  real Q0;
  real Q;
  real df;
  real rad_width;
  real tot_width;
  real sigma_freq;

  real kDoppler;
  real KE_shift;

  real activity;
  real rate_log;
  real total_rate;

  vector[nBinEvents] rate;

  real dm21;
  real dm32;
  real dm31;

  real s12;
  real s13;

  vector[nFamily] m_nu;
  vector[nFamily] U_PMNS;
  real<lower = 0.> neutrino_mass;

  real<lower=25., upper=35.> T0;     // Average of temperature distribution, given temp calibration (K)
  real<lower=25., upper=35.> temp;   // Temperature of source gas (K)
  real<lower=0.0> deltaT_total;      // Used only for calculation of delta_sigma, as check (K)


  real<lower=0.0> lambda;   // Fraction of T2 component of source in ortho (odd rotation) state
  real<lower=0.0> epsilon;  // Fractional activity of source gas compared to pure T_2
  real<lower=0.0> kappa;    // Ratio of HT to DT
  real<lower=0.0> eta;      // Composition fraction of T (eta = f_T/(f_T2+f_HT+f_DT))

  real<lower=0.0> composition[num_iso]; //Simplex of fractional composition of each isotopolog: (f_T2,f_HT,f_DT, f_T)

  real<lower=0.0> sigma_floating;         // Best estimate, from theory, for standard deviation of Q distribution (eV)
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
  # Here is where the model from Talia should be added

  T0 <- vnormal_lp(Tparam1, T_set, deltaT_calibration);
  temp <- vnormal_lp(Tparam2, T0, deltaT_fluctuation);

  lambda <- vnormal_lp(lambda_param, lambda_set, delta_lambda);
  epsilon <- vnormal_lp(epsilon_param, epsilon_set, delta_epsilon);
  kappa <- vnormal_lp(kappa_param, kappa_set, delta_kappa);

  if (delta_eta != 0.0){
    eta <- vnormal_lp(eta_param, eta_set, delta_eta);}

    deltaT_total <- pow(pow(deltaT_calibration, 2) + pow(deltaT_fluctuation, 2), 0.5);

    composition <- find_composition(epsilon, kappa, eta, num_iso);
    composition_set <- find_composition(epsilon_set, kappa_set, eta_set, num_iso);

    // Determine total rate from activity
    for (j in 1:num_iso){
      activity <- tritium_rate_per_eV() * beta_integral(Q_T_molecule[i], neutrino_mass, minKE) * number_density * effective_volume / (tritium_halflife() / log(2.) );
      total_rate <- mu_tot * activity * measuring_time;

      df <- vnormal_lp(uF, 0.0, sigma_freq);
      for (i in 1:nBinEvents){
        frequency <- freq_data[i] - df + fclock;

        KE <- get_kinetic_energy(frequency, MainField);

        kDoppler <-  m_electron() * get_velocity(QValue) * sqrt(eDop / tritium_molecular_mass());

        KE_shift <- KE - kDoppler;

        //   Determine signal and background rates from beta function and background level
        rate_log <- signal_to_noise_log(KE_shift, Q, U_PMNS, m_nu , minKE, maxKE, signal_fraction);
        rate[i] <- total_rate * exp(rate_log);
      }
    }

  }

  model {

    #  Thermal Doppler broadening of the tritium source

    eDop ~ gamma(1.5,1./(k_boltzmann() * temperature));

    for (i in 1:nBinTime)
    {
      if(n_time_data[i]!=0)
      {
        n_time_data[i] ~ normal( n0_timeData * exp( - time_data[i] * scatt_width ) , sqrt( n_time_data[i]*1. ) );
      }
    }

    mu_tot ~ uniform(0.5 ,1.5);
    for (i in 1:nBinEvents)
    {
      if(rate[i]!=0)
      {
        n_events[i] ~ poisson(rate[i]);
      }
    }


  }

  generated quantities {

  }
