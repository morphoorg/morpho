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
  real BFieldError;

  //   Range for fits (in Hz)

  real<lower=0 > minKE;
  real<lower=minKE> maxKE;

  //   Endpoint of tritium, in eV

  real<lower=minKE,upper=maxKE> QValue;
  real<lower=0> sigmaQ;

  //  Cross-section of e-T2 , in meter^-2

  real xsec_avekin;
  real xsec_bindkin;
  real xsec_msq;
  real xsec_Q;

  //  Conditions of the experiment and measurement

  real number_density;			//  Tritium number density (in meter^-3)
  real temperature;				//  Temperature of gas (in Kelvin)
  real effective_volume;		        //  Effective volume (in meter^3)
  real measuring_time;			//  Measuring time (in seconds)

  //  Background rate

  real background_rate;			//  Background rate in Hz

  //  Clock and filter information

  real fBandpass;
  real fclockError;
  int  fFilterN;
  // real fclock;

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

}

parameters {

  real uB;
  real uQ;
  real uF;
  real<lower=0.0> eDop;
  real<lower=0.0> duration;
  real<lower=minKE,upper=maxKE> KE;
}

transformed parameters{

  real neutrino_mass;
  real signal_rate;
  real<lower=0> MainField;
  real beta;
  real Q;
  real df;
  real frequency;

  real xsec;
  real<lower=0> scatt_width;
  real rad_width;
  real tot_width;

  real sigma_freq;
  real freq_recon;
  // real freq_temp;

  real kDoppler;
  real KE_shift;

  real activity;
  real signal_fraction;
  real total_rate;
  real rate_log;
  real rate;

  // Determine effective mass to use from neutrino mass matrix

  neutrino_mass <- sqrt(dot_self(U_PMNS .* m_nu));

  // Obtain magnetic field (with prior distribution)

  MainField <- vnormal_lp(uB, BField, BFieldError);

  // Calculate scattering length, radiation width, and total width;

  beta <- get_velocity(KE);
  xsec <- xsection(KE,  xsec_avekin, xsec_bindkin, xsec_msq, xsec_Q);
  scatt_width <- number_density * c() * beta * xsec;

  rad_width <- cyclotron_rad(MainField);
  tot_width <- (scatt_width + rad_width);
  sigma_freq <- (scatt_width + rad_width) / (4. * pi());

  // Dispersion due to uncertainty in final states (with prior distribution)

  Q <- vnormal_lp(uQ, QValue, sigmaQ);

  // Calculate frequency dispersion

  frequency <- get_frequency(KE, MainField);

  df <- vnormal_lp(uF, 0.0, sigma_freq);

  // freq_temp <- frequency-df;
  freq_recon <- frequency + df - fclock;

  // Calculate Doppler effect from tritium atom/molecule motion

  kDoppler <-  m_electron() * beta * sqrt(eDop / tritium_molecular_mass());

  KE_shift <- KE + kDoppler;

  // Determine total rate from activity

  activity <- tritium_rate_per_eV() * beta_integral(Q, neutrino_mass, minKE) * number_density * effective_volume / (tritium_halflife() / log(2.) );
  total_rate <-activity * measuring_time;
  signal_fraction <- activity/(activity + background_rate);

  // Determine signal and background rates from beta function and background level

  rate_log <- signal_to_noise_log(KE_shift, Q, U_PMNS, m_nu, minKE, maxKE, signal_fraction);
  rate <- total_rate * exp(rate_log);
}

model {

  // KE ~ uniform(minKE,maxKE);
  # Thermal Doppler broadening of the tritium source

  eDop ~ gamma(1.5,1./(k_boltzmann() * temperature));

  # Frequency broadening from collision and radiation

  duration ~ exponential(scatt_width);

  # Effect of filter in cleaning data

  // freq_recon ~ filter(0., fBandpass, fFilterN);
  freq_recon ~ uniform(minFreq,maxFreq);

  # The Poisson distribution of the beta decay and background if desired
  # Otherwise set to flat distribution if nGenerate is negative

  if (nGenerate >= 0) increment_log_prob(rate_log);

}

generated quantities {

  int isOK;
  int nData;
  int  events;
  real freq_data;
  real time_data;
  real rate_data;
  real KE_recon;

  nData <- nGenerate;

  #   Simulate duration of event and store frequency and reconstructed kinetic energy

  time_data <- duration;

  freq_data <- freq_recon;

  KE_recon <- get_kinetic_energy(frequency+df, MainField);

  # Compute the number of events that should be simulated for a given frequency/energy.  Assume Poisson distribution.

  rate_data <- rate;

  events <- poisson_rng(rate / max(abs(nGenerate*nChains),nChains) );

  # Tag events that are below DC in analysis

  isOK <- (freq_data > 0.);

}
