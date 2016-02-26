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
* Defines functions and constants used in beta decay spectrum neutrino mass generation and analysis models.
*
*/


functions{

// Finds vector of squares of PMNS matrix elements U_e

vector matrix_elements(real meas_th12, real meas_th13) {
vector[3] sUe_fixed;

sUe_fixed[1] <- square(cos(meas_th12)*cos(meas_th13));
sUe_fixed[2] <- square(sin(meas_th12)*cos(meas_th13));
sUe_fixed[3] <- square(sin(meas_th13));

return sUe_fixed;
}

// Finds vector of neutrino masses (m1, m2, m3) assuming one mass hierarchy with fixed minimum mass

vector MH_masses(real min_mass_fixed, real meas_delta_m21, real meas_delta_m32, int MH) {
vector[3] nu_mass_fixed;
//<lower=0.0, upper=0.5>

// Defining neutrino masses assuming NH is true
if (MH==0){
nu_mass_fixed[1] <- min_mass_fixed;
nu_mass_fixed[2] <- sqrt(square(min_mass_fixed)+meas_delta_m32-meas_delta_m21);
nu_mass_fixed[3] <- sqrt(square(min_mass_fixed)+meas_delta_m32);
//nu_mass_fixed[2] <- sqrt(square(min_mass_fixed)+meas_delta_m21);
//nu_mass_fixed[3] <- sqrt(square(min_mass_fixed)+meas_delta_m21+meas_delta_m32);
}
// Defining neutrino masses assuming IH is true
else if (MH==1){
nu_mass_fixed[3] <- min_mass_fixed;
nu_mass_fixed[1] <- sqrt(square(min_mass_fixed)+meas_delta_m32-meas_delta_m21);
nu_mass_fixed[2] <- sqrt(square(min_mass_fixed)+meas_delta_m32);

}
else
print ("MH=0 for normal hierarchy; MH=1 for inverted hierarchy");

return nu_mass_fixed;
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

// Method for generating beta decay spectrum with a flat background (larger signal fraction -> less background)
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